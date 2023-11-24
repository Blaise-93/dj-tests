from leads.models import Agent
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class AgentModelForm(forms.ModelForm):
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
        
