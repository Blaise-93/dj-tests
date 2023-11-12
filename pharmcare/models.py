from django.db import models
from songs.models import User
from leads.models import Lead, Agent




# PHARMACEUTICALS MGMT - CARE PLAN TODO

class PharmaceuticalCarePlan(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)

    patients = models.ManyToManyField('Patient')
    patient_unique_code = models.CharField(max_length=20)

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


class Patient(models.Model):

    medical_charge = models.PositiveBigIntegerField(blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    leads = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True)
    patient_details = models.OneToOneField(
        'PatientDetail', on_delete=models.CASCADE)

    medical_history = models.OneToOneField('MedicationHistory',
                                           on_delete=models.SET_NULL, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class PatientDetail(models.Model):
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
    marital_status = models.CharField(
        max_length=20, choices=MARITAL_STATUS, default='Single')
    patient_class = models.CharField(
        max_length=20, choices=PATIENT_STATE, default='Adult')
    age = models.PositiveIntegerField()
    agent = models.ForeignKey(
        Agent, on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name='Pharmacist')
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10)
    height = models.CharField(max_length=20)
    BMI = models.CharField(max_length=10)
    patient_history = models.TextField(editable=True)
    past_medical_history = models.CharField(
        max_length=500, null=True, blank=True)
    social_history = models.CharField(max_length=250)
    slug = models.SlugField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f'{self.first_name} {self.last_name[0:1]}. \
            : {self.age} old {self.gender} with {self.BMI} BMI. '


class MedicationHistory(models.Model):
    
    class Meta:
        verbose_name_plural = 'Medication History'
    medication_list = models.CharField(max_length=600)
    indication_and_evidence = models.CharField(max_length=600)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        medical_history = self.medication_list[:25]
        return f'patient history in abbreviated format: {medical_history}'


class ProgressNote(models.Model):
    notes = models.TextField(editable=True, verbose_name="patient's note")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        notes = self.notes[:30]
        return f'patient notes in abbreviated format: {notes}'


class MedicationChanges(models.Model):

    class Meta:
        verbose_name_plural = 'Medication Changes'

    medication_list = models.CharField(max_length=50)
    dose = models.CharField(max_length=30)
    frequency = models.CharField(max_length=30, default='BD')
    route = models.CharField(max_length=20, default='Oral')
    indication = models.CharField(max_length=200, null=True, blank=True)
    start_or_continued_date = models.CharField(
        max_length=50, verbose_name='Start/Continued Date')
    stop_date = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'patient medication: {self.dose} dose to be taken via {self.route}'


class MonitoringPlan(models.Model):
    parameter_used = models.CharField(max_length=100)
    justification = models.CharField(max_length=300)
    frequency = models.CharField(
        max_length=100, default='On admission and then 6 hours after',
        verbose_name='Result(s) and Action Plan')
    results_and_action_plan = models.CharField(max_length=300)
    has_improved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.parameter_used


class AnalysisOfClinicalProblem(models.Model):

    class Meta:
        verbose_name_plural = 'Analysis of Clinical Problems'

    PRORITY_CHOICES = (
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    )

    clinical_problem = models.CharField(max_length=50)
    assessment = models.CharField(max_length=50)
    priority = models.CharField(max_length=50, choices=PRORITY_CHOICES)
    action_taken_or_future_plan = models.CharField(
        max_length=500, verbose_name='Action Taken/Future Plan')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.clinical_problem[:30]


class FollowUpPlan(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    follow_up_requirement = models.CharField(max_length=100)
    action_taken_and_future_plan = models.CharField(max_length=100,
                                                    verbose_name="Action Taken/Future Plan")
    state_of_improvement_by_score = models.CharField(max_length=4,
                                                     default='70%')
    has_improved_than_before = models.BooleanField(default=False)
    adhered_to_medications_given = models.BooleanField(default=False)
    referral = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'''
            {self.user.username} state of improvement by score is
            {self.state_of_improvement_by_score}
        '''
