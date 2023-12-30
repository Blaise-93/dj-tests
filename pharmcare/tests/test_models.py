from django.test import TestCase, TransactionTestCase
from pharmcare.models import *
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from staff.models import User
from leads.models import UserProfile


class PatientDetailTest(TestCase):
    """ Unit tests for our Patient details of our model """

    @classmethod
    def setUpClass(self):
        # set up non-modified patientdetail object used by
        # by all class method: this action is performed once 
        
        # python manage.py test pharmcare.tests.test_models
        
                
        self.user, created = User.objects.get_or_create(
             username='blaise',
             first_name='test_first_name',
             last_name='test_last_name',
             email='test_email',
             password='test_password'
        )
        
        #user = User.objects.get(id=1).username
        
        profile_user = UserProfile.objects.create(user=self.user)
        print(profile_user)
    
        
        PatientDetail.objects.create(
            first_name='John',
            last_name='Philips',
            email='johnphilips@gmail.com',
            marital_status='marital_status',
            patient_class='adult',
            organization=profile_user.user.first_name,
            gender='male',
            age=60,
            weight=78,
            height=6,
            patient_history='Philip patient_history',
            past_medical_history='BP patient',
            social_history='smoker',
            slug='3e4r5t6y7ufds',
            phone_number='08076543487',
            consultation=1000
        )
        
      
    
    def test_patient_detail_first_name(self):
        patient_detail =  PatientDetail.objects.get(id=1)
        patient_field_label = patient_detail._meta.\
            get_field('john'.title()).verbose_name
        self.assertEqual(patient_field_label, "John")
        
    
    
    



