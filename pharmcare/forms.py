from django import forms
from pharmcare.models import *
from tinymce.widgets import admin_widgets

class PatientDetailForm(forms.ModelForm):
    class Meta:
        
       
        model = PatientDetail
        fields = [
                'first_name',
                'last_name',
                'email',
                'marital_status', 
                'patient_class',
                'age',
                'pharmacist',
                'gender',
                'height',
                'BMI',
                'patient_history',
                'past_medical_history',
                'social_history',
                'slug',
                'phone_number',
                'pharm_care_fee'
              
        ]
        