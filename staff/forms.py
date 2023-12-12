from django import forms
from .models import Management, Attendance
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class AttendanceModelForm(forms.ModelForm):
    """ A form class responsible for the staff daily records form creation in the database
    in realtime"""
    class Meta:
        model = Attendance
        fields = [
            'full_name',
            'sign_in_time',
            'sign_out_time',
            'date_added',
            'staff_attendance_ref',
            'organization' ,
            'management', 
        ]

class ManagementModelForm(forms.ModelForm):
    """ form class that handles organization management form for the attendance
    if the user is granted access."""
    class Meta:
        model = User
        fields = [
       
            'username',
            'first_name',
            "last_name",
            'email',
               
        ]
        
        labels = {
            "username": "Enter your username",
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            'email': 'Enter your email',
        }
        