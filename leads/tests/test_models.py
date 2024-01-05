from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from songs.models import User
from utils import slug_modifier,files
from leads.models import UserProfile, Lead, Agent, Category


# Lead Test

class LeadTest(TestCase):
    """ Unit tests for the Lead of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified leads object used by
         by all class method: this action is performed once '''

        # python manage.py test pharmcare.tests.test_models {setUpTestData (read more)}
        super(LeadTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Chinwe',
            first_name='Chinwe',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.category_1 = Category.objects.create(
            name="New",
            organization=profile_user,
            slug=slug_modifier()
        )
        
        cls.category_2 = Category.objects.create(
            name="Unconverted",
            organization=profile_user,
            slug=slug_modifier()
        )
        
        
        cls.lead_1 = Lead.objects.create(
            first_name='John',
            last_name='Okafor',
            email='johnokafor@gmail.com',
            organization=profile_user,
            agent=None,
            slug=slug_modifier(),
            phone_number='08046543487',
            category=cls.category_1,
            social_media_accounts='Facebook',
            phoned=True,
            description="Hi there, any thing for me today?",
            address="21 Avenue Road, Abuja",
            files=files('songs/mails/subscription.txt'),
            date_added=timezone.now() - timedelta(hours=1) 
        )
        
        
        cls.lead_2 = Lead.objects.create(
            first_name='Onyekwelu',
            last_name='Ijeoma',
            email='onyekweluijeoma@gmail.com',
            organization=profile_user,
            agent=None,
            slug=slug_modifier(),
            phone_number='08033243487',
            category=cls.category_2,
            social_media_accounts='Twitter',
            phoned=True,
            description="Hi there. Her name is Ijeoma, a sale's rep.",
            address="20 Avenue Road, Abuja",
            files=files('songs/mails/subscription.txt'),
            date_added=timezone.now() - timedelta(hours=1) 
        )

    def test_leads_full_name(self):
        """Test full_name of the first lead collated by the organizer before 
        assigning it to the agent"""

        
        self\
        .assertEqual(f'{self.lead_1.first_name} {self.lead_1.last_name} '.strip(),  
                     "John Okafor")

    def test_leads_description(self):
        """test and assert that lead has the verbose name as claimed field
        in the model
        """

        lead_1 = Lead.objects.get(id=1)
        leads_field_label = lead_1._meta.get_field(
            'description').auto_created
        leads_field_label_name = lead_1._meta.get_field(
            'description').verbose_name
        self.assertEqual(leads_field_label, False)
        self.assertEqual(leads_field_label_name, 'description')

    def test_leads_detail_email(self):
        """ assert the marital status length given """
        lead2 = Lead.objects.get(id=2)
        email = lead2._meta.get_field(
            'email').max_length
        self.assertEqual(email, 100)

    def test_leads_detail_first_name(self):
        """ function that test first_name field """
        lead_1 = Lead.objects.get(id=1)
        leads_field_label = lead_1.\
            _meta.get_field('first_name').verbose_name

        self.assertEqual(leads_field_label, "first name")

    def test_user_profile(self):
        """ function that test user profile of our model,which get called when created
        by the organizer..."""
        UserProfile.objects.get_or_create(user=self.user)
        self.assertEqual(self.user.userprofile.user.username, 'Chinwe')

    def test_get_leads_detail_absolute_url(self):
        """ function that test that leads detail absolute url is correct as claimed 

        NB: The leads first_name which was created will dynamically be inserted in the
        slug as the first value before slug modifier will be added up as a string."""

        lead_1 = Lead.objects.get(id=1)
        absolute_url = f'/leads/{lead_1.slug}/'
        self.assertEqual(lead_1.get_absolute_url(), absolute_url)

    

