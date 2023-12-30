from django.test import TestCase
#from .forms import UserForm
from pharmcare.forms import PatientDetailModelForm
from songs.models import User
from decimal import Decimal
#from .models import User

class PatientDetailFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.\
            create(
                username='blaise',
                first_name='test_first_name',
                last_name='test_last_name',
                email='test_email',
                password='test_password',
                phone_number=3005678
             )
            
        
            

    def test_form_valid(self):
        form = PatientDetailFormTest(
                data={
                'username': "blaise",
                'password': "test_password",
                'first_name': "test_first_name",
                'phone': 3005678
            }, 
                instance=self.user
            )
        self.assertTrue(form.is_valid())
