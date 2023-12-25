from django.db import models
from songs.models import User
from django.shortcuts import get_object_or_404
from leads.models import Lead, Agent, UserProfile
from django.db import models
from datetime import datetime, timedelta
from functools import reduce
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify
from utils import slug_modifier, generate_patient_unique_code


# PHARMACEUTICALS MGMT - CARE PLAN TODO

class PharmaceuticalCarePlan(models.Model):
    """ 
     A complex table with relationship mapping to other table to 
     keep patients pharmacauticall care plan in our database.
     Each patient is assigned to a unique patient code to better 
     identify the records of the user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pharmacist = models.ForeignKey(
        "Pharmacist", on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE)
    patients = models.ManyToManyField('Patient')
    patient_unique_code = models.CharField(
        max_length=20, null=True, blank=True)

    # abstract patient full name from base patients (manytomany orm) manager
    # prior to saving the entry to the db, and it is a nullable field.
    patient_full_name = models.CharField(max_length=20, null=True, blank=True)
    has_improved = models.BooleanField(default=False,
                                       verbose_name="has improved (tick good, if yes, otherwise don't.)")
    progress_note = models.ForeignKey(
        'ProgressNote', on_delete=models.SET_NULL, blank=True, null=True)
    medication_changes = models.ForeignKey(
        'MedicationChanges', on_delete=models.SET_NULL, blank=True, null=True)

    analysis_of_clinical_problem = models.ForeignKey(
        'AnalysisOfClinicalProblem', on_delete=models.SET_NULL, blank=True, null=True)

    monitoring_plan = models.ForeignKey(
        'MonitoringPlan', on_delete=models.SET_NULL, blank=True, null=True)
    follow_up_plan = models.ForeignKey(
        'FollowUpPlan', on_delete=models.SET_NULL, blank=True, null=True)
    total_payment = models.PositiveBigIntegerField(null=True, blank=True)
    discount = models\
        .PositiveBigIntegerField(null=True, blank=True,
                                 help_text="discount given to patient,\
            perhaps due to his/her consistent loyalty, if any.")

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.monitoring_plan.frequency

    def get_pharmcare_absolute_url(self):
        reverse("pharmcare:patients-detail",
                kwargs={"pk": self.pk})

    def get_analysis_of_clinical_problem(self) -> str:
        if self.analysis_of_clinical_problem:
            return self.analysis_of_clinical_problem
        return 'Not yet provided'

    def get_medication_changes(self) -> str:
        if self.medication_changes:
            return self.medication_changes
        return 'Not yet provided'

    def get_monitoring_plan(self) -> str:
        if self.monitoring_plan:
            return self. monitoring_plan
        return 'Not yet provided'

    def get_follow_up_plan(self) -> str:
        if self.follow_up_plan:
            return self.follow_up_plan
        return 'Not yet provided'

    def get_progress_note(self) -> str:
        if self.progress_note:
            return self.progress_note
        return 'Not yet provided'

    def get_total(self) -> int:
        patient_pharmcare_summary = PharmaceuticalCarePlan.objects.filter(
            id=self.pk)
        # pt_name = Patient.objects.get(id=self.pk)
        total = 0
        for patient_list in patient_pharmcare_summary:
            for patient_list in self.patients.all():
                
                total += patient_list.get_total_charge()

            if self.discount:
                # check discount if any
                if total > self.discount:
                    total -= self.discount
                    print(total)
            return total

    def get_utc_by_date(self):
        if self.date_created.now() >= 17:
            return self.date_created.now()

    def save(self, *args, **kwargs):
        self.total_payment = self.get_total()
        return super().save(self, *args, **kwargs)

    def get_patient_fullname(self, request, slug):
        """ a helper function to dynamically abstract each patient
        full name and force it to be saved in our db."""
        # get the id of the patients from patientdetail table
        item = get_object_or_404(PatientDetail, slug=slug)

        # get  or create the patient queryset which is a
        # a many to many model.
        patient_qs, created = Patient.objects.get_or_create(
            user=request.user, patient=item
        )
        # filter out the user making the request
        # and check  whether the object exist
        pharmcare_qs = PharmaceuticalCarePlan.objects.filter(user=request.user)

        if pharmcare_qs.exists():

            patients_qs = pharmcare_qs[0]
            if patients_qs.patients.filter(patient__slug=item.slug).exists():

                # for items in self.patients.all():

                first_name = patient_qs.patient.first_name
                last_name = patient_qs.patient.last_name
                if len(full_name) <= 20:
                    full_name = f'{first_name} {last_name}'
                    print(full_name)
                else:
                    full_name = f'{first_name} {last_name[:1].capitalize()}'
                print(full_name)
                return full_name

        return self.patients

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.patient_unique_code:

            self.patient_unique_code = generate_patient_unique_code()
            # self.patient_full_name = self.get_patient_fullname()
            self.total_payment = self.get_total()

        super().save(*args, **kwargs)


class Patient(models.Model):
    """ Patient model which has a many to many attribute to dynamically map out each
    patients/user details, medication history and customer leads in our db 

    Methods & arguments it has are:
         `get_total_charge()`: is a function that sums up the pharmacist's consultation fee
        if any and add it up to the drug cost price (amount paid) made by the patient.
        However, it checks whether the conditions are met before it does the summation as 
        you can see below.

        ```python
         def get_total_charge(self) -> int:
            total = 0
            # check whether there is additional charges like drug price to be added
            # if yes, then add medical charges to the total
            if self.medical_charge:
                amount_charged = self.patient.consultation + self.medical_charge
                total += amount_charged
                return total
            total += self.patient.consultation
            return total

        ```

        `save()` : commit and overide the total if the user did not sum it up prior to 
        saving the patient data.
    """

    medical_charge = models.PositiveBigIntegerField(blank=True, null=True,
                                                    verbose_name="amount paid (medical charge if any)")
    notes = models.TextField(null=True, blank=True)

    pharmacist = models.ForeignKey(
        "Pharmacist", on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    patient = models.ForeignKey(
        'PatientDetail', on_delete=models.CASCADE,
        verbose_name='Patient-detail')

    medical_history = models.ForeignKey(
        'MedicationHistory',
        on_delete=models.CASCADE)

    total = models.PositiveBigIntegerField(editable=True, blank=True,
                                           null=True, verbose_name="Total (auto-add)")
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.patient.first_name

    def get_medical_charge(self):
        if self.medical_charge:
            return f'₦{self.medical_charge}'
        return 'Nill'

    def get_west_african_time_zone(self):
        """ converts the utc time to West African time for the user 
        on the frontend - however, the admin panel still maintained 
        UTC+0 time integrity."""
        date_time = datetime.strptime(
            str(self.date_created.date()), '%Y-%m-%d')
        lagos_time = date_time + timedelta(hours=2)

        return lagos_time

    def get_full_name(self):
        return f'{self.patient.first_name} {self.patient.last_name}'

    def get_total_charge(self) -> int:
        total = 0
        # check whether there is additional charges like drug price to be added
        # if yes, then add medical charges to the total
        if self.medical_charge:
            amount_charged = self.patient.consultation + self.medical_charge
            total += amount_charged
            return total
        total += self.patient.consultation
        return total

    def save(self, *args, **kwargs):
        # commit and overide the total if the user did not sum it up prior to
       # saving the patient data.
        self.total = self.get_total_charge()
        super().save(self, *args, **kwargs)

    def sum_number(acc, total): return acc + total  # sum numbers fn
    """  def get_cummulative(self):
        cumm_total = reduce(self.sum_number, self.get_total_charge())
        print(cumm_total)
        return cumm_total  """


class PatientDetail(models.Model):

    """
    Patient detail model::
    This helps us to set a table for each patients with a column for 
    respective medical data specific for them for further query and examination 
    in our organization.  

    For example, here we determine the gender of our patient, names,
    patient class, BMI etc. However, if the client has already existed in our database on
    our lead table, then we will collect their data from there without asking them some
    basic useful information like names etc. 

     Important information:
        - Not all collected leads of our clients are actually patients, so that's why we 
    have a separate model to better record our patients and give them all the medical
    support they need during the pharmaceutical care process.
        - Some clients can later turn to patient in the future so keeping the leads
        record separately is great so that you can know who came in the pharmacy or the 
        organization and at what time.



    """

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),

    )

    MARITAL_STATUS = (
        ("Married", "Married"),
        ("Single", "Single"),
        ("Married with Kids", "Married with Kids"),
        ("Married without Kids", "Married without Kids"),
        ("Divorced", "Divorced"),
        ("Single Parent", "Single Parent"),
        ("Other", "Other"),

    )

    PATIENT_STATE = (
        ("Adult", "Adult"),
        ("Child", "Child"),
        ("Toddler", "Toddler"),
        ("Adolescent", "Adolescent"),
        ("Elderly", "Elderly")



    )

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(max_length=30, null=True, blank=True)
    marital_status = models.CharField(
        max_length=20, choices=MARITAL_STATUS, default='Single')
    patient_class = models.CharField(
        max_length=20, choices=PATIENT_STATE, default='Adult')
    age = models.PositiveIntegerField(validators=[MinValueValidator(0),
                                                  MaxValueValidator(150)])
    pharmacist = models.ForeignKey(
        "Pharmacist", on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Pharmacist')
    organization = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE)
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10)
    height = models.FloatField(null=True, blank=True, editable=True,
                               help_text="must be provided in ft",
                               error_messages="Kindly provide the patient's")
    weight = models.FloatField(null=True, blank=True,
                               help_text="must be provided in kg",
                               editable=True,
                               error_messages="Kindly provide the patient's weight")
    BMI = models.CharField(max_length=10)
    patient_history = models.TextField(editable=True, blank=False)
    past_medical_history = models.CharField(
        max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True,
                                    validators=[MinValueValidator("01010000000"),
                                                MaxValueValidator("09991000000")])
    consultation = models.PositiveBigIntegerField(null=True, blank=True)
    social_history = models.CharField(
        max_length=250, editable=True, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def get_email(self):
        if self.email is not None:
            return self.email
        return 'No email provided'

    def get_west_african_time(self):
        """ converts the utc time to West African time for the user 
        on the frontend - however, the admin panel still maintained 
        UTC+0 time integrity."""
        date_time = datetime.strptime(
            str(self.date_created.date()), '%Y-%m-%d')
        lagos_time = date_time + timedelta(hours=2)

        return lagos_time

    def get_patient_weight(self):
        if self.weight is not None:
            return f'{self.weight}kg'
        return 'No weight provided'

    def get_patient_height(self):

        if self.height is not None:
            return f'{self.height}ft'
        return 'No weight provided'

    def patients_bmi(self) -> int:

        # check whether the user input the correct units
        # of weight and height.
        if self.height and self.weight is not None:
            # check if the said height of a patient is greater than 0 foot
            if self.height > 0:
                square_foot = 0.3048  # in m2 based on metric conversion
                in_meter_square = (self.height * square_foot)
                bmi = round((self.weight) /
                            (in_meter_square * in_meter_square), 2)

                return f'{bmi}kg/m2'

        return f"Not provided"

    def get_absolute_url(self):
        return reverse("pharmcare:patient-detail", kwargs={"slug": self.slug})

    def __str__(self):

        return f'{self.first_name} {self.last_name[0:1]}. \
            : {self.age} old {self.gender} with {self.BMI} BMI. '

    def save(self, *args, **kwargs):
        """ override the original save method to set the patient details 
        according to if agent has phoned or not"""
        # patient_detail = PatientDetail.objects.filter(
        #    slug=self.slug)

       # for i in patient_detail:

        self.BMI = self.patients_bmi()
        self.slug = slugify(
            f'{(self.first_name + slug_modifier())}')

        super().save(*args, **kwargs)


class Pharmacist(models.Model):
    """ Pharmacist in our model. Pharmacists are assigned to each patient
     to manage and engage them with solemn pharmaceutical care plan.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=12,
                                    validators=[MinValueValidator("010100000"),
                                                MaxValueValidator("099010100000")])
    email = models.EmailField(max_length=30, unique=True)
    slug = models.SlugField()
    organization = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username

    def get_west_african_time_zone(self):
        """ converts the utc time to West African time for the user 
        on the frontend - however, the admin panel still maintained 
        UTC+0 time integrity."""
        date_time = datetime.strptime(
            str(self.date_joined.date()), '%Y-%m-%d')
        lagos_time = date_time + timedelta(hours=2)
        return lagos_time

    def save(self, *args, **kwargs):
        """ override the original save method to set the lead 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{self.first_name + slug_modifier()}', allow_unicode=False)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('managements:managements-detail', kwargs={
            'slug': self.slug
        })


class MedicationHistory(models.Model):
    """ A model that handles all our patients detail medical history """
    class Meta:
        verbose_name_plural = 'Medication History'
        ordering = ['id',]

    medication_list = models.CharField(max_length=600)
    indication_and_evidence = models.CharField(max_length=600)
    slug = models.SlugField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        medical_history = self.medication_list[:50]
        return f'patient history in abbreviated format: {medical_history}...'

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(*args, **kwargs)

    def get_medication_absolute_url(self):
        return reverse("pharmcare:medication-history-detail",
                       kwargs={"pk": self.pk})


class ProgressNote(models.Model):
    """ Model class that handles the progress note of each patient. """
    class Meta:
        ordering = ['id',]

    notes = models.TextField(editable=True, verbose_name="patient's note")
    date_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    def __str__(self) -> str:
        notes = self.notes[:30]
        return f'patient notes in abbreviated format: {notes}...'

    def get_west_african_time(self):
        """ converts the utc time to West African time for the user 
        on the frontend - however, the admin panel still maintained 
        UTC+0 time integrity."""
        date_time = datetime.strptime(
            # work on this - 2023-12-03 02:00:00 -> strip the hour
            str(self.date_created.date().today()), '%Y-%m-%d')
        lagos_time = date_time + timedelta(hours=2)
        print(lagos_time)
        return lagos_time

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(*args, **kwargs)


class MedicationChanges(models.Model):
    """ a model class for patients posology """
    class Meta:
        verbose_name_plural = 'Medication Changes'
        ordering = ['id']

    medication_list = models.CharField(max_length=100)
    dose = models.CharField(max_length=150)
    frequency = models.CharField(max_length=30, default='BD')
    route = models.CharField(max_length=20, default='Oral')
    slug = models.SlugField()
    indication = models.CharField(max_length=200, null=True, blank=True)
    start_or_continued_date = models.CharField(blank=False,
                                               max_length=50, verbose_name='Start/Continued Date')
    stop_date = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'patient medication: {self.dose} dose to be taken via {self.route}'

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(*args, **kwargs)


class MonitoringPlan(models.Model):
    """ Monitoring plan is our model class schema that handles all the required data used
    to monitor patients plan and justification of the patient wellbeing."""

    class Meta:
        ordering = ['id',]
    parameter_used = models.CharField(max_length=100)
    justification = models.CharField(max_length=300)
    frequency = models.CharField(
        max_length=100, default='On admission and then 6 hours after',
        verbose_name='Result(s) and Action Plan')
    results_and_action_plan = models.CharField(max_length=300)
    slug = models.SlugField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.parameter_used

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(*args, **kwargs)


class AnalysisOfClinicalProblem(models.Model):
    """ Analysis of clinical Problem is a model class schema that handles 
    clinical challanges encountered during the course of the treatment of our patient."""

    class Meta:
        verbose_name_plural = 'Analysis of Clinical Problems'
        ordering = ['id',]

    PRORITY_CHOICES = (
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    )

    clinical_problem = models.CharField(max_length=50)
    assessment = models.CharField(max_length=50)
    priority = models.CharField(max_length=50, choices=PRORITY_CHOICES)
    slug = models.SlugField()
    action_taken_or_future_plan = models.CharField(
        max_length=500, verbose_name='Action Taken/Future Plan')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.clinical_problem[:30]

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(*args, **kwargs)


class FollowUpPlan(models.Model):
    """ Follow up plan model class collates all the basic information a
    pharmacist needs to further follow up the case if needs be.

    NB:
        `patient` -> a nullable foriegn key variable is left nullable in case
    the pharmacist decide not to record the patient he/she is following up 
    at the moment which he/she must select when handling pharmaceutical schema. 
    """

    class Meta:
        ordering = ['id',]

    patient = models.ForeignKey(PatientDetail,
                                on_delete=models.SET_NULL, blank=True, null=True)
    follow_up_requirement = models.CharField(max_length=100)
    action_taken_and_future_plan = models.CharField(max_length=100,
                                                    verbose_name="Action Taken/Future Plan")
    state_of_improvement_by_score = models.CharField(max_length=4,
                                                     default='for example -> 70%')
    has_improved_than_before = models.BooleanField(default=False)
    slug = models.SlugField()
    adhered_to_medications_given = models.BooleanField(default=False)
    referral = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:

        return f'''
            state of improvement by score is
            {self.state_of_improvement_by_score}

        '''

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(*args, **kwargs)


class Team(models.Model):
    """ Team model in our db """
    class Meta:
        verbose_name_plural = 'Med-Connect Staff'
    full_name = models.CharField(max_length=50, verbose_name="Full name")
    position = models.CharField(max_length=25)
    image = models.ImageField()
    description = models.CharField(max_length=200)
    alt_description = models.CharField(max_length=60)
    facebook_aria_label = models.CharField(max_length=30)
    twitter_aria_label = models.CharField(max_length=30)
    instagram_aria_label = models.CharField(max_length=30)
    facebook_link = models.CharField(max_length=150, unique=True)
    instagram_link = models.CharField(max_length=150, unique=True)
    twitter_link = models.CharField(max_length=150, unique=True)
    chat = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name}'
