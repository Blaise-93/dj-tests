from django import forms
from leads.models import Lead
from songs.models import User
from django.contrib.auth.forms import UserCreationForm, UsernameField

class LeadForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    age = forms.IntegerField(min_value=1)
    
class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "first_name",
            "last_name",
            "age",
            'agent'
            
        ]
        
class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = { "username": UsernameField }


    