from django import forms
from .models import Song, Category, Subscribe


class SubscribedModelForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = [
            'email'
        ]