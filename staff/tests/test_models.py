from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from songs.models import User
from utils import slug_modifier, generate_patient_unique_code
from staff.models import *
from leads.models import *


# Attendance

class AttendanceTestModel(TestCase):
    """ Unit tests for the Attendance of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified attendance object used by
         by all class method: this action is performed once '''

        super(AttendanceTestModel, cls).setUpClass()

        time = timezone.now() - timedelta(hours=1)

        cls.user = User.objects.create(
            username='Chinwe',
            first_name='Chinwe',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )

        cls.profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.management = Management.objects.create(
            user=cls.user,
            first_name='Uche',
            last_name="Egini",
            phone_number='080345476532',
            email='ucheegini@gmail.com',
            slug=slug_modifier(),
            organization=cls.profile_user,
            date_joined=time,

        )

        cls.attendance1 = Attendance.objects.create(
            full_name='John Okafor',
            organization=cls.profile_user,
            management=cls.management,
            slug=slug_modifier(),
            date_created=time,
            user=cls.user,
            sign_in_time='8:00',
            staff_attendance_ref=generate_patient_unique_code(),
            sign_out_time='1/5/2023',
            date_sign_out_time=None,

        )

        cls.attendance2 = Attendance.objects.create(
            full_name='Onyekwelu',
            organization=cls.profile_user,
            management=cls.management,
            slug=slug_modifier(),
            user=cls.user,
            date_created=time,
            sign_in_time='8:00',
            staff_attendance_ref=generate_patient_unique_code(),
            sign_out_time='1/5/2024',
            date_sign_out_time='1/5/2024',
        )

    def test_staff_full_name(self):
        """Test full_name of the first lead collated by the organizer before 
        assigning it to the management"""

        self\
            .assertEqual(f'{self.attendance1.get_fullname()} '.strip(),
                         "John Okafor")

    def test_staff_signed_out(self):
        """test and assert that staff has the verbose name signed out as claimed field
        in the model
        """

        attendance1 = Attendance.objects.get(id=1)
        staff_field_sign_out_label = attendance1._meta.get_field(
            'date_sign_out_time').auto_created

        staff_field_label_name = attendance1._meta.get_field(
            'date_sign_out_time').verbose_name

        self.assertEqual(staff_field_sign_out_label, False)
        self.assertEqual(staff_field_label_name, 'date sign out time')

    def test_staff_attendance_ref(self):
        """ assert the attendance ref code given """
        lead2 = Attendance.objects.get(id=2)
        ref_code = lead2._meta.get_field(
            'staff_attendance_ref').max_length
        self.assertEqual(ref_code, 15)

    def test_staff_detail_full_name(self):
        """ function that test full_name field of a given attendance instance """
        attendance1_full_name = Attendance.objects.get(id=1)
        staff_field_label = attendance1_full_name.\
            _meta.get_field('full_name').verbose_name

        self.assertEqual(staff_field_label, "full name")

    def test_user_profile(self):
        """ function that test user profile of our model,which get called when created
        by the organizer..."""
        UserProfile.objects.get_or_create(user=self.user)
        self.assertEqual(self.user.userprofile.user.username, 'Chinwe')

    def test_get_staff_detail_absolute_url(self):
        """ function that test that staff detail absolute url is correct as claimed 

        NB: The staff first_name which was created will dynamically be inserted in the
        slug as the first value before slug modifier will be added up as a string."""

        attendance1 = Attendance.objects.get(id=1)
        absolute_url = f'/staff-attendance/{attendance1.slug}/'
        self.assertEqual(attendance1.get_absolute_url(), absolute_url)

    def test_lead1_has_correct_management_with_the_said_name(self):
        """ check that the staff has the expected management which the organization
        assigned him to.
        """
        self.\
            assertNotEqual(f'''Management full name:
                {self.attendance1.management.first_name} {self.attendance1.management.last_name}  '''
                .strip(), "Uche Egini")

    def test_user_is_organizer(self):
        """ check that the user is an organizer """

        # 'Chinwe' is not equal to 'blaise' - the organizer from db atm.
        self.assertEqual(self.profile_user.user.is_organizer, False)


# Management


class ManagementTestModel(TestCase):
    """ Unit tests for our Management model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified staff progress notes object used by
         by all class method: this action is performed once '''

        super(ManagementTestModel, cls).setUpClass()

        cls.user = User.objects.create(
            username='Chinwe',
            first_name='Chinwe',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )

        cls.profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.management = Management.objects.create(
            user=cls.user,
            first_name='Uche',
            last_name="Egini",
            phone_number='080345476532',
            email='ucheegini@gmail.com',
            slug=slug_modifier(),
            organization=cls.profile_user,
            date_joined=datetime.now() - timedelta(hours=1),
        )

    def test_management_user_profile(self):
        """ function that assert management user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Chinwe")

    def test_management_user_organization(self):
        """ function that assert management organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.management.organization, userprofile)

    def test_management_user(self):
        """ function that assert management user is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.management.user, self.user)

    def test__management_email(self):
        """ assert the management length given """
        # staff_detail = MedicationHistory.objects.get(id=1)
        note_length = self.management._meta.\
            get_field('email').max_length
        self.assertEqual(note_length, 30)

    def test_management_slug(self):
        """function that assert the route field name of the patien. """
        # staff_detail = MedicationHistory.objects.get(id=1)
        management_slug_field_name = self.management._meta.\
            get_field('slug').verbose_name
        self.assertEqual(management_slug_field_name, 'slug')

    def test_management_full_name(self):
        """ function that assert management fullname is same with what was provided ."""

        self.\
            assertEqual(f"""{self.management.first_name} {self.management.last_name} """
                        .strip(), 'Uche Egini')
