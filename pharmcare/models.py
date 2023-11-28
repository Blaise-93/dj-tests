from django.db import models
from songs.models import User
from leads.models import Lead, Agent, UserProfile
from django.db import models
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
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)

    patients = models.ManyToManyField('Patient')
    patient_unique_code = models.CharField(max_length=20)
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

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.patient_unique_code:

            self.patient_unique_code = generate_patient_unique_code()

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
    leads = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True)
    pharmacist = models.ForeignKey(
        Agent, on_delete=models.SET_NULL, null=True,
        blank=True, verbose_name='Pharmacist')
    patient = models.OneToOneField(
        'PatientDetail', on_delete=models.CASCADE)

    medical_history = models.OneToOneField(
        'MedicationHistory',
        on_delete=models.CASCADE)
    total = models.PositiveBigIntegerField(editable=True, blank=True,
                                           null=True, verbose_name="Total (auto-add)")

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.patient.first_name

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

    def get_cummulative(self):
        total = 0

        total += self.get_total_charge

        return total


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

    class Meta:
        ordering = ['id']

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
    email = models.CharField(max_length=20, null=True, blank=True)
    marital_status = models.CharField(
        max_length=20, choices=MARITAL_STATUS, default='Single')
    patient_class = models.CharField(
        max_length=20, choices=PATIENT_STATE, default='Adult')
    age = models.PositiveIntegerField()
    pharmacist = models.ForeignKey(
        Agent, on_delete=models.SET_NULL, null=True,
        blank=True, verbose_name='Pharmacist')
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10)
    height = models.CharField(max_length=20)
    BMI = models.CharField(max_length=10)
    patient_history = models.TextField(editable=True, blank=False)
    past_medical_history = models.CharField(
        max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    consultation = models.PositiveBigIntegerField(null=True, blank=True)
    social_history = models.CharField(max_length=250, editable=True)
    slug = models.SlugField()
    date_created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("pharmcare:patient-detail", kwargs={"slug": self.slug})

    def __str__(self):

        return f'{self.first_name} {self.last_name[0:1]}. \
            : {self.age} old {self.gender} with {self.BMI} BMI. '

    def save(self, *args, **kwargs):
        """ override the original save method to set the patient details 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{(self.first_name + slug_modifier())}')

        super().save(*args, **kwargs)


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

    def get_absolute_url(self):
        return reverse("pharmcare:medication-history-detail",
                       kwargs={"pk": self.pk})


class ProgressNote(models.Model):
    class Meta:
        ordering = ['id',]

    notes = models.TextField(editable=True, verbose_name="patient's note")
    date_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self) -> str:
        notes = self.notes[:30]
        return f'patient notes in abbreviated format: {notes}...'

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(self, *args, **kwargs)


class MedicationChanges(models.Model):
    """ a model class for patients posology """
    class Meta:
        verbose_name_plural = 'Medication Changes'
        ordering = ['id']

    medication_list = models.CharField(max_length=50)
    dose = models.CharField(max_length=30)
    frequency = models.CharField(max_length=30, default='BD')
    route = models.CharField(max_length=20, default='Oral')
    slug = models.SlugField(null=True, blank=True)
    indication = models.CharField(max_length=200, null=True, blank=True)
    start_or_continued_date = models.CharField(
        max_length=50, verbose_name='Start/Continued Date')
    stop_date = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'patient medication: {self.dose} dose to be taken via {self.route}'

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(self, *args, **kwargs)


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
    slug = models.SlugField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.parameter_used

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(self, *args, **kwargs)


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
    slug = models.SlugField(null=True, blank=True)
    action_taken_or_future_plan = models.CharField(
        max_length=500, verbose_name='Action Taken/Future Plan')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.clinical_problem[:30]

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(self, *args, **kwargs)


class FollowUpPlan(models.Model):
    """ Follow up plan model class collates all the basic information a
    pharmacist needs to further follow up the case if needs be."""

    class Meta:
        ordering = ['id',]

    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    follow_up_requirement = models.CharField(max_length=100)
    action_taken_and_future_plan = models.CharField(max_length=100,
                                                    verbose_name="Action Taken/Future Plan")
    state_of_improvement_by_score = models.CharField(max_length=4,
                                                     default='70%')
    has_improved_than_before = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)
    adhered_to_medications_given = models.BooleanField(default=False)
    referral = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'''
            {self.user.username} state of improvement by score is
            {self.state_of_improvement_by_score}
        '''

    def save(self, *args, **kwargs):
        self.slug = slug_modifier()
        super().save(self, *args, **kwargs)
