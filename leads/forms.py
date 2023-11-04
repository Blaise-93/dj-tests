from django import forms
from leads.models import Lead, Agent, Category
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
            'agent',
            "phoned",
            'phone_number',
            'description',
            'email',
            'social_media_accounts'


        ]


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}


class AgentAssignedForm(forms.Form):
    agent = forms.ModelChoiceField(
        queryset=Agent.objects.none()
    )

    def __init__(self, *args, **kwargs):

        request = kwargs.pop('request')
        agent = Agent.objects.filter(organization=request.user.userprofile)
        super(AgentAssignedForm, self).__init__(*args, **kwargs)
        self.fields['agent'].queryset = agent


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'category'
        ]

class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
              'name',
           
        ]