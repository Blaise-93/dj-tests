from django import forms
from leads.models import Lead, Agent, Category, Contact
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
            'social_media_accounts',
            'address',
            'files',
            'slug'
        ]

        labels = {

            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "age": 'Enter your age',
            'phone_number': 'Enter your phone number',
            'description': 'Enter your discription',
            'email': 'Enter your email',
            'address': " Enter your address",
            'slug': "Enter your client's first name as the slug",
        }


class ContactUsForm(forms.ModelForm):
    """ A prepopulated contact form to handle all
    the form submission by our users/patients."""
    class Meta:
        model = Contact

        help_texts = {
            'full_name': "Enter your full name",
            'subject': "Kindly enter your request subject...",
            'message': 'Kindly express your words to us...'
        }

        fields = [
            'full_name',
            'country',
            'subject',
            'message'
        ]


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}


class AgentAssignedForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

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
        labels = {
            'name': 'Enter the category name',
            'slug': "Enter the category's slug"
        }
        
        fields = [
            'name',
            'slug'

        ]
