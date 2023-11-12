from django import forms
from pharmcare.models import *

class PatientDetailForm(forms.ModelForm):
    class Meta:
        models = PatientDetail
        fields = [
                'first_name',
                'last_name',
                'marital_status', 
                'patient_class,'
                'age',
                'agent',
                'gender',
                'height',
                'BMI',
                'patient_history',
                'past_medical_history',
                'social_history',
                'slug',
                'date_created',
        ]