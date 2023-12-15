from django import forms
from .models import Management, Attendance
from django import forms
from django.contrib.auth import get_user_model
from leads.forms import CustomUserForm

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
            'organization',
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


class ManagementAssignedForm(forms.Form):
    management = forms.ModelChoiceField(queryset=Management.objects.none())

    def __init__(self, *args, **kwargs):

        request = kwargs.pop('request')
        management = Management.objects.filter(organization=request.user.userprofile)
      
        super(ManagementAssignedForm, self).__init__(*args, **kwargs)
       
        self.fields['management'].queryset = management

