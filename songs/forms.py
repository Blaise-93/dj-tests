from django import forms
from .models import Song, Category, Subscribe
from tinymce.widgets import TinyMCE

class SubscribedModelForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = [
            'email'
        ]
        
class SubscribedForm(forms.Form):
    email = forms.EmailField(max_length=30)
    
class NewsletterForm(forms.Form):
    subject = forms.CharField()
    receivers = forms.CharField()
    message = forms.CharField(widget=TinyMCE(), label="Email content")
