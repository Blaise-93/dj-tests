from rest_framework import serializers
from .models import Lead

class LeadSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Lead
        fields = [
            'first_name',
            "last_name",
            "age",
            'agent',
             "phoned",
            'phone_number',
            'description',
            'email',
            'social_media_accounts'
        ]
        
