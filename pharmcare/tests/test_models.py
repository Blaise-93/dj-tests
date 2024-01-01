from django.test import TestCase
from pharmcare.models import *
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from songs.models import User
from utils import slug_modifier
from leads.models import UserProfile


class PatientDetailTest(TestCase):
    """ Unit tests for our Patient details of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patientdetail object used by
         by all class method: this action is performed once '''

        # python manage.py test pharmcare.tests.test_models {setUpTestData (read more)}
        super(PatientDetailTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Blaise',
            first_name='Blaise',
            last_name='Ejike',
            email='test_email',
            password='test_password'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.patient_detail = PatientDetail.objects.create(
            first_name='John',
            last_name='Philips',
            email='johnphilips@gmail.com',
            marital_status='marital_status',
            patient_class='adult',
            organization=profile_user,
            gender='male',
            age=60,
            weight=78,
            height=6,
            BMI=None,
            patient_history='Philip patient_history',
            past_medical_history='BP patient',
            social_history='smoker',
            slug=slug_modifier(),
            phone_number='08076543487',
            consultation=1000
        )

    def test_patient_bmi(self):
        """bmi test function to help us assert the patient bmi if provided """
        patient_detail = PatientDetail.objects.get(id=1)

        no_bmi = "Not provided"

        if patient_detail.height and patient_detail.weight is not None:
            if patient_detail.height > 0:
                # height in BMI must be in feet
                square_foot = 0.3048  # in m2 based on metric conversion
                in_meter_square = (patient_detail.height * square_foot)
                pt_bmi = round((patient_detail.weight) /
                               (in_meter_square * in_meter_square), 2)

                # must pass assertion for bmi calculated
                self.assertEqual(f'{pt_bmi}kg/m2',  '23.32kg/m2')
                # print(f'{pt_bmi}kg/m2')

        # if height and weight of the patient is not provided
        self.assertEqual(f'{no_bmi}',  'Not provided')

    def test_patient_history(self):
        """ assert whether the patient has the provided medical history 


        NB: The only autocreated field in our patient_detail db table
        we have is  date_created field 
        """

        patient_detail = PatientDetail.objects.get(id=1)
        patient_field_label = patient_detail._meta.get_field(
            'patient_history').auto_created
        patient_field_label_name = patient_detail._meta.get_field(
            'patient_history').verbose_name
        self.assertEqual(patient_field_label, False)
        self.assertEqual(patient_field_label_name, 'patient history')

    def test_patient_detail_marital_status(self):
        """ assert the marital status length given """
        patient_detail = PatientDetail.objects.get(id=1)
        marital_status = patient_detail._meta.get_field('marital_status').max_length
        self.assertEqual(marital_status, 20)
        
        
    def test_patient_detail_first_name(self):
        """ function that test first_name field """
        patient_detail = PatientDetail.objects.get(id=1)
        patient_field_label = patient_detail.\
            _meta.get_field('first_name').verbose_name

        self.assertEqual(patient_field_label, "first name")

    def test_user_profile(self):
        """ function that test user profile of our model,which get called when created
        by the organizer..."""
        UserProfile.objects.get_or_create(user=self.user)
        self.assertEqual(self.user.userprofile.user.username, 'Blaise')

    def test_get_patient_detail_absolute_url(self):
        """ function that test that patient detail absolute url is correct as claimed 
        
        NB: The patient first_name which was created will dynamically be inserted in the
        slug as the first value before slug modifier will be added up as a string."""
        
        patient_detail = PatientDetail.objects.get(id=1)
        absolute_url = f'/pharmcare/{patient_detail.slug}/'
        self.assertEqual(patient_detail.get_absolute_url(), absolute_url)
        
    def test_consultation_fee(cls):
        """ assert that consultation fee is what that was claimed in the db """
        cls.assertEqual(cls.patient_detail.consultation, 1000)
        