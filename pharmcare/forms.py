from django import forms
from pharmcare.models import *
from tinymce.widgets import admin_widgets
from django.contrib.auth import get_user_model

User = get_user_model()


class PatientDetailModelForm(forms.ModelForm):
    """ Patient detail form is a form class that helps us to input, check the validility
    of the form prior to it's submission of our patient's details given. """
    class Meta:

        model = PatientDetail
        fields = [
            'first_name',
            'last_name',
            'email',
            'marital_status',
            'patient_class',
            'gender',
            'age',
            "weight",
            'height',
            'patient_history',
            'past_medical_history',
            'social_history',
            'slug',
            'phone_number',
            'consultation'

        ]

        labels = {
            'first_name': 'Enter your patient\'s first name',
            'last_name': 'Enter your patient\'s last name',
            'email': ' Enter your patient\'s email if any',
            'age': ' Enter your patient\'s age',
            'height': "Enter your patient's height in (feet)",
            'weight': "Enter your patient's weight in (kg)",
            'patient_history':  "Enter your patient's medical history",
            'past_medical_history': "Enter your patient's past medical history",
            'social_history': 'Enter the social history of your patient if any',
            'slug': "Enter your patient's first name as the slug",
            'phone_number': 'Enter your patient\'s phone number',
            'consultation': 'Enter the consultation fee if any'
        }


class MedicationHistoryForm(forms.ModelForm):
    """ patients form for medication history """

    class Meta:
        model = MedicationHistory

        fields = [
            'medication_list',
            'indication_and_evidence'
        ]
        labels = {
            'medication_list': " Enter your patient's medication list",
            'indication_and_evidence': "Enter your patient's indication"
        }

        labels = {
            'medical_charge': "Enter medical charge",
            'notes': "Enter patient's notes to follow up on your next possible action ",
            'patient': "Select patient for this field which you had previously created",
            'medical_history': 'Select patient medical history for this field which you had previously created',
            'total': 'Optional (the summation is done instantenously)',
        }


class ProgressNoteForm(forms.ModelForm):
    """ patients form for medication history """

    class Meta:
        model = ProgressNote

        fields = [
            'notes'
        ]
        labels = {
            'notes': "Enter your patient's medical notes "
        }
        error_messages = {
            'error': "Kindly input the patient note, Pharm."
        }


class MedicationChangesForm(forms.ModelForm):
    """ Medication changes form is a form class that handles all the form field and submissions
    made by the pharmacist wrt patient posology/changes due to the mediactions that s/he is placed on."""
    class Meta:
        model = MedicationChanges

        fields = [
            'medication_list',
            'dose',
            'frequency',
            'route',
            'indication',
            'stop_date',

        ]

        labels = {
            'medication_list': "Enter the list of medications you want to dispense to your patient",
            'dose': "Enter the dose of the medication",
            'frequency': " Enter the frequency of the dose",
            'route': " Enter the route of administration of the drug ",
            'indication': " Enter the drug(s) indication",
            'start_or_continued_date': " (Optional) If the time is left blank, it will automatically generated",
            'stop_date': " Enter the time the patient is meant to stop the drug",

        }
        error_messages = {
            'error': "Kindly input the patient fields, Pharm."
        }


class AnalysisOfClinicalProblemForm(forms.ModelForm):
    """ Analysis of Clinical Problem form is a form class that helps us to input, check the validility
    of the form prior to it's submission of our patient's clinical problems retrieved from the model. """
    class Meta:
        model = AnalysisOfClinicalProblem

        fields = [
            "clinical_problem",
            "assessment",
            "priority",
            "action_taken_or_future_plan",
        ]

        labels = {
            "clinical_problem": " Enter the patient's clinical problem(s)",
            "assessment": 'Enter your clinical assessment about patient',
            "priority": "Choose the priority",
            "action_taken_or_future_plan": "Enter action to be taken concerning the patient",

        }
        error_messages = {
            'error': f"Kindly input the patient fields, Pharm."
        }


class MonitoringPlanForm(forms.ModelForm):
    """ Monitoring plan form is a form class that helps us to input, check the validility
    of the form prior to it's submission of our patient's monitoring plan retrieved from the model. """

    class Meta:
        model = MonitoringPlan
        fields = [
            'parameter_used',
            'justification',
            'frequency',
            'results_and_action_plan'
        ]


class FollowUpPlanForm(forms.ModelForm):
    """ Analysis of Clinical Problem form is a form class that helps us to input, check the validility
    of the form prior to it's submission of our patient's clinical problems retrieved from the model. """

    class Meta:
        model = FollowUpPlan

        fields = [

            'follow_up_requirement',
            'action_taken_and_future_plan',
            'state_of_improvement_by_score',
            'has_improved_than_before',
            'adhered_to_medications_given',
            'referral'
        ]

        labels = {
            'user': "Enter the user ( Optional )",
            'follow_up_requirement': " Enter the follow up requirement for the patient",
            "action_taken_or_future_plan": "Enter action to be taken concerning the patient",
            'state_of_improvement_by_score': "Score the patient's medical improvement by percent ",
            'referral': " Enter the referral's name. "
        }
        error_messages = {
            'error': f"Kindly input the patient fields, Pharm."
        }


class PatientModelForm(forms.ModelForm):
    """ class that handles the patient form input and submission in our db made by our pharmacist.  """
    class Meta:
        model = Patient
        fields = [
            'medical_charge',
            'notes',
            #  'pharmacist',
            'patient',
            'medical_history',
            # 'total',
        ]


class PharmaceuticalCarePlanModelForm(forms.ModelForm):
    """ Pharmceutical care form that handles user input and validations """
    class Meta:
        model = PharmaceuticalCarePlan
        fields = [
            'patients',
            'has_improved',
            'progress_note',
            'medication_changes',
            'analysis_of_clinical_problem',
            'monitoring_plan',
            'follow_up_plan',
            'discount'
        ]


""" PharmacistModelForm, PharmacistAssignedForm """

# Pharmacist Forms


class PharmacistModelForm(forms.ModelForm):
    """ form class that handles organization pharmacist form for the patient
    if the user is granted access."""

    class Meta:
        model = User

        fields = [

            'username',
            'first_name',
            "last_name",
            'phone_number',
            'email',

        ]

        labels = {
            "username": "Enter your username",
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "phone_number": "Enter your phone number",
            'email': 'Enter your email',
        }


class PharmacistAssignedForm(forms.Form):
    pharmacist = forms.ModelChoiceField(queryset=Pharmacist.objects.none())

    def __init__(self, *args, **kwargs):

        request = kwargs.pop('request')
        pharmacist = Pharmacist.objects.filter(
            organization=request.user.userprofile)

        super(PharmacistAssignedForm, self).__init__(*args, **kwargs)

        self.fields['pharmacist'].queryset = pharmacist
