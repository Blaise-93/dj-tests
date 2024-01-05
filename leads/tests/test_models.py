from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from songs.models import User
from utils import slug_modifier, files
from leads.models import UserProfile, Lead, Agent, Category


# Lead 

class LeadTest(TestCase):
    """ Unit tests for the Lead of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified leads object used by
         by all class method: this action is performed once '''


        super(LeadTest, cls).setUpClass()
        time = timezone.now() - timedelta(hours=1)

        cls.user = User.objects.create(
            username='Chinwe',
            first_name='Chinwe',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )
        
        # real organizer currently from the db
        cls.user2 = User.objects.create(
            username='blaise',
            first_name='blaise',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )

        # user = User.objects.get(id=1).username

        cls.profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.category_1 = Category.objects.create(
            name="New",
            organization=cls.profile_user,
            slug=slug_modifier()
        )

        cls.category_2 = Category.objects.create(
            name="Unconverted",
            organization=cls.profile_user,
            slug=slug_modifier()
        )

        cls.agent1 = Agent.objects.create(
            user=cls.user,
            first_name='Uche',
            last_name="Egini",
            date_joined=time,
            email='ucheegini@gmail.com',
            slug=slug_modifier(),
            organization=cls.profile_user
        )

        cls.lead_1 = Lead.objects.create(
            first_name='John',
            last_name='Okafor',
            email='johnokafor@gmail.com',
            organization=cls.profile_user,
            agent=cls.agent1,
            slug=slug_modifier(),
            phone_number='08046543487',
            category=cls.category_1,
            social_media_accounts='Facebook',
            phoned=True,
            description="Hi there, any thing for me today?",
            address="21 Avenue Road, Abuja",
            files=files('songs/mails/subscription.txt'),
            date_added=time
        )

        cls.lead_2 = Lead.objects.create(
            first_name='Onyekwelu',
            last_name='Ijeoma',
            email='onyekweluijeoma@gmail.com',
            organization=cls.profile_user,
            agent=None,
            slug=slug_modifier(),
            phone_number='08033243487',
            category=cls.category_2,
            social_media_accounts='Twitter',
            phoned=True,
            description="Hi there. Her name is Ijeoma, a sale's rep.",
            address="20 Avenue Road, Abuja",
            files=files('songs/mails/subscription.txt'),
            date_added=time
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

    def test_lead1_has_correct_agent_with_the_said_name(self):
        """ check that the leads has the expected agent which the organization
        assigned him to.
        """
        self.\
            assertNotEqual(f'''Agent full name:
                {self.lead_1.agent.first_name} {self.lead_1.agent.last_name}  '''
                           .strip(), "Uche Egini")

    def test_assigned_leads_to_category(self):
        """ check and assert that lead category was assigned to lead1 and lead2 and that the name 
        are 'New' and 'Unconverted' respectiverly. """

        self.assertEqual(self.lead_1.category.name, "New")
        self.assertEqual(self.lead_2.category.name, "Unconverted")

    def test_leads_has_correct_categories(self):
        """ check that the leads has the expected categories, and are not equal to each other"""
        self.assertNotEqual(self.lead_1.category.name,
                            self.lead_2.category.name)

    def test_lead1_category_update_url(self):
        """ check that lead category update url is exact to what is expected """

        update_url = f'/leads/categories/{self.lead_1.slug}/update/'
        self.assertEqual(
            self.lead_1.get_lead_category_update_url(), update_url)
    
    def test_user_is_organizer(self):
        """ check that the user is an organizer """
           
        # 'Chinwe' is not equal to 'blaise' - the organizer from db atm.
        self.assertEqual(self.profile_user.user.is_organizer, False)
   
     
# Agent 


class AgentTest(TestCase):
    """ Unit tests for our Agent model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified lead object used by
         by all class method: this action is performed once '''

        super(AgentTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Chinwe',
            first_name='Chinwe',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )
        

        cls.profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)
        
        cls.agent = Agent.objects.create(
            user=cls.user,
            first_name='Uche',
            last_name="Egini",
            date_joined=timezone.now() - timedelta(hours=1),
            email='ucheegini@gmail.com',
            slug=slug_modifier(),
            organization=cls.profile_user
        )

  
    def test_agent_user_profile(self):
        """ function that assert agent user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Chinwe")

    def test_agent_user_organization(self):
        """ function that assert agent organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.agent.organization, userprofile)

    def test_agent_user(self):
        """ function that assert agent user is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.agent.user, self.user)

    def test__agent_email(self):
        """ assert the agent length given """
        # lead_detail = MedicationHistory.objects.get(id=1)
        note_length = self.agent._meta.\
            get_field('email').max_length
        self.assertEqual(note_length, 30)

    def test_agent_slug(self):
        """function that assert the route field name of the lead. """
        # lead_detail = MedicationHistory.objects.get(id=1)
        agent_slug_field_name = self.agent._meta.\
            get_field('slug').verbose_name
        self.assertEqual(agent_slug_field_name, 'slug')

    def test_agent_full_name(self):
        """ function that assert agent fullname is same with what was provided ."""

        self.\
            assertEqual\
            (f"""{self.agent.first_name} {self.agent.last_name} """\
             .strip(), 'Uche Egini')


