from django.test import TestCase
from pharmcare.models import *
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from songs.models import User
from utils import slug_modifier
from leads.models import UserProfile


# Patient Details

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
        marital_status = patient_detail._meta.get_field(
            'marital_status').max_length
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


# Patient history
class MedicationHistoryTest(TestCase):
    """ Unit tests for our Patient medical history of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient medicationhistory object used by
         by all class method: this action is performed once '''

        super(MedicationHistoryTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.medical_history = MedicationHistory.objects.create(
            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            medication_list="Amatem softgel, Paractamol",
            indication_and_evidence="For treatment of malaria and fever",
            slug=slug_modifier(),
            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

       # print(cls.medical_history.date_created)

    def test_med_history_user_profile(self):
        """ function that assert med history user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_med_history_user_organization(self):
        """ function that assert med history organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.medical_history.organization, userprofile)

    def test_med_history_user(self):
        """ function that assert med history organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.medical_history.user, self.user)

    def test_med_history_medication_list(self):
        """ assert the medication list length given """
        # patient_detail = MedicationHistory.objects.get(id=1)
        medication_list_length = self.medical_history._meta.\
            get_field('medication_list').max_length
        self.assertEqual(medication_list_length, 600)

    def test_med_history_indication_and_evidence(self):
        """function that assert the indication_and_evidence field name  """
        # patient_detail = MedicationHistory.objects.get(id=1)
        indication_and_evidence_field_name = self.medical_history._meta.\
            get_field('indication_and_evidence').verbose_name
        self.assertEqual(indication_and_evidence_field_name,
                         "indication and evidence")

    def test_get_med_history_absolute_url(self):
        """ function that test that patient medical history absolute url is 
        correct as claimed 
        """

        absolute_url = f'/pharmcare/medication-history/{
            self.medical_history.pk}/'
        self.assertEqual(
            self.medical_history.get_medication_absolute_url(), absolute_url)


# Medication Changes
class MedicationChangesTest(TestCase):
    """ Unit tests for our Patient medication changes of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient medication changes object used by
         by all class method: this action is performed once '''

        super(MedicationChangesTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.medication_changes = MedicationChanges.objects.create(
            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            medication_list="Amatem softgel, Paractamol",
            dose='Amatem 500mg',
            frequency='BD',
            route='oral',
            slug=slug_modifier(),
            start_or_continued_date='12/12/2023',
            stop_date='10/1/2024',

            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

    def test_med_changes_user_profile(self):
        """ function that assert med history user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_med_changes_user_organization(self):
        """ function that assert med changes organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.medication_changes.organization, userprofile)

    def test_med_changes_user(self):
        """ function that assert medication changes organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.medication_changes.user, self.user)

    def test_med_changes_medication_list(self):
        """ assert the medication list length given """
        # patient_detail = MedicationHistory.objects.get(id=1)
        medication_list_length = self.medication_changes._meta.\
            get_field('medication_list').max_length
        self.assertEqual(medication_list_length, 100)

    def test_med_changes_route(self):
        """function that assert the route field name of the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        med_route_field_name = self.medication_changes._meta.\
            get_field('route').verbose_name
        self.assertEqual(med_route_field_name, "route")

    def test_med_changes_stop_date(self):
        """function that assert the route field name of the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        stop_date_field_name = self.medication_changes._meta.\
            get_field('stop_date').attname
        self.assertEqual(stop_date_field_name, "stop_date")

# Progress Note


class ProgressNoteTest(TestCase):
    """ Unit tests for our Patient progress notes of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient progress notes object used by
         by all class method: this action is performed once '''

        super(ProgressNoteTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.progress_notes = ProgressNote.objects.create(
            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            notes='Hello my patient\'s note',
            slug=slug_modifier(),
            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

    def test_progress_note_user_profile(self):
        """ function that assert patient progress note user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_progress_note_user_organization(self):
        """ function that assert progress note organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.progress_notes.organization, userprofile)

    def test_progress_note_user(self):
        """ function that assert medication changes organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.progress_notes.user, self.user)

    def test_patient_progress_note(self):
        """ assert the medication list length given """
        # patient_detail = MedicationHistory.objects.get(id=1)
        note_length = self.progress_notes._meta.\
            get_field('notes').max_length
        self.assertEqual(note_length, None)

    def test_progress_note_slug(self):
        """function that assert the route field name of the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        progress_slug_field_name = self.progress_notes._meta.\
            get_field('slug').verbose_name
        self.assertEqual(progress_slug_field_name, 'slug')


# Monitoring plan

class MonitoringPlanTest(TestCase):
    """ Unit tests for our Patient monitoring plan of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient monitoring plan object used by
         by all class method: this action is performed once '''

        super(MonitoringPlanTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.monitoring_plan = MonitoringPlan.objects.create(
            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            slug=slug_modifier(),
            parameter_used=" patient parameter used",
            justification="justification of the patient",
            frequency="BD",
            results_and_action_plan='results and action plan',

            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

    def test_monitoring_plan_parameter_used(self):
        """ assert the medication list length given """
        # patient_detail = MedicationHistory.objects.get(id=1)
        parameter_used_length = self.monitoring_plan._meta.\
            get_field('parameter_used').max_length
        self.assertEqual(parameter_used_length, 100)

    def test_monitoring_plan_justification(self):
        """function that assert the justification field name of the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        justification_field_name = self.monitoring_plan._meta.\
            get_field('justification').verbose_name
        self.assertEqual(justification_field_name, "justification")

    def test_monitoring_plan_result_and_action(self):
        """function that assert the result and action field name of the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        results_and_action_plan_field_name = self.monitoring_plan._meta.\
            get_field('results_and_action_plan').attname
        self.assertEqual(results_and_action_plan_field_name,
                         "results_and_action_plan")

    def test_monitoring_plan_user_profile(self):
        """ function that assert monitoring plan user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_monitoring_plan_user_organization(self):
        """ function that assert monitoring plan organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.monitoring_plan.organization, userprofile)

    def test_monitoring_plan_user(self):
        """ function that assert monitoring plan organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.monitoring_plan.user, self.user)


# Analysis of Clinical Problem

class AnalysisofClinicalProblemTest(TestCase):
    """ Unit tests for our analysis of clinical problem of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient analysis of clinical problem object used by
         by all class method: this action is performed once '''

        super(AnalysisofClinicalProblemTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

        # user = User.objects.get(id=1).username

        profile_user, created = UserProfile.objects.get_or_create(
            user=cls.user)

        cls.analysis_of_cp = AnalysisOfClinicalProblem.objects.create(
            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            slug=slug_modifier(),
            clinical_problem='clinical problem',
            assessment='the assessment',
            priority='prioritized patient health challanges',
            action_taken_or_future_plan='take future action if any',

            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

    def test_analysis_of_cp_issue(self):
        """ assert the clinical problem list length given """
        # patient_detail = MedicationHistory.objects.get(id=1)
        analysis_of_cp_length = self.analysis_of_cp._meta.\
            get_field('clinical_problem').max_length
        self.assertEqual(analysis_of_cp_length, 50)

    def test_analysis_of_cp_assessment(self):
        """function that assert the justification field name of the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        assessment_field_name = self.analysis_of_cp._meta.\
            get_field('assessment').verbose_name
        self.assertEqual(assessment_field_name, "assessment")

    def test_analysis_of_cp_result_and_action(self):
        """function that assert the result and action field name of
        the patient. """
        # patient_detail = MedicationHistory.objects.get(id=1)
        action_taken_or_future_plan_field_name = self.analysis_of_cp._meta.\
            get_field('action_taken_or_future_plan').attname
        self.assertEqual(action_taken_or_future_plan_field_name,
                         "action_taken_or_future_plan")

    def test_analysis_of_cp_user_profile(self):
        """ function that assert analysis of clinical problem user profile 
        username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_analysis_of_cp_user_organization(self):
        """ function that assert analysis of clinical problem organization
        is same with the  userprofile during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.analysis_of_cp.organization, userprofile)

    def test_analysis_of_cp_user(self):
        """ function that assert analysis of clinical problem organization is
        same with the  userprofile during post_save signal instance."""

        self.assertEqual(self.analysis_of_cp.user, self.user)


# Follow up Plan
class FollowUpPlanTest(TestCase):
    """ Unit tests for our Patient follow up plan of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient follow up plan object used by
         by all class method: this action is performed once '''

        super(FollowUpPlanTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

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

        cls.follow_up_plan = FollowUpPlan.objects.create(

            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            slug=slug_modifier(),
            patient=cls.patient_detail,
            follow_up_requirement='follow up plan',
            action_taken_and_future_plan='action taken and future plan',
            state_of_improvement_by_score='state of improvement by score',
            has_improved_than_before=True,
            adhered_to_medications_given=True,
            referral='UNTH',

            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

    def test_follow_up_plan_state_of_improvement_by_score(self):
        """ assert the state of improvement by score length given """

        state_of_improvement_by_score_length = self.follow_up_plan._meta.\
            get_field('state_of_improvement_by_score').max_length
        self.assertEqual(state_of_improvement_by_score_length, 3)

    def test_follow_up_plan_has_improved_than_before(self):
        """function that assert the has improved than before field name of the patient. """

        has_improved_than_before_field_name = self.follow_up_plan._meta.\
            get_field('has_improved_than_before').verbose_name
        self.assertEqual(has_improved_than_before_field_name,
                         "has improved than before")

    def test_follow_up_plan_referral(self):
        """function that assert the result and action field name of the patient. """

        referral_field_name = self.follow_up_plan._meta.\
            get_field('referral').attname
        self.assertEqual(referral_field_name,
                         "referral")

    def test_follow_up_plan_user_profile(self):
        """ function that assert follow up plan user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_follow_up_plan_user_organization(self):
        """ function that assert follow up plan  organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.follow_up_plan.organization, userprofile)

    def test_follow_up_plan_user(self):
        """ function that assert follow up plan  organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.follow_up_plan.user, self.user)

    def test_follow_up_plan_patient_name(self):
        """ function that assert follow up plan  organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.follow_up_plan.patient.first_name,
                         self.patient_detail.first_name)


# Patient - Many to Many Relationship Model

class PatientTest(TestCase):
    """ Unit tests for our Patient follow up plan of our model """

    @classmethod
    def setUpClass(cls):
        ''' set up non-modified patient follow up plan object used by
         by all class method: this action is performed once '''

        super(PatientTest, cls).setUpClass()

        cls.user = User.objects.create(
            username='Bruno',
            first_name='Bruno',
            last_name='Marz',
            email='test_email',
            password='test_password'
        )

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

        cls.medical_history = MedicationHistory.objects.create(
            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            medication_list="Amatem softgel, Paractamol",
            indication_and_evidence="For treatment of malaria and fever",
            slug=slug_modifier(),
            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

        cls.patients = Patient.objects.create(

            user=cls.user,
            pharmacist=None,
            organization=profile_user,
            slug=slug_modifier(),
            patient=cls.patient_detail,
            medical_charge=5000,
            notes="patient notes",
            medical_history=cls.medical_history,
            total=None,

            # utc date time
            date_created=timezone.now() - timedelta(hours=1)
        )

    def test_patients_notes(self):
        """ assert the state of notes length given """
        notes_length = self.patients._meta.\
            get_field('notes').max_length

        # NB - patient notes was not given
        self.assertNotEqual(notes_length, 200)

    def test_patients_slug(self):
        """function that assert the slug field name of the patient. """

        slug_field_name = self.patients._meta.\
            get_field('slug').verbose_name
        self.assertEqual(slug_field_name,
                         "slug")

    def test_patients_total(self):
        """function that assert the total payment of the patient. """
        total = 0
        if self.patients.medical_charge:
            total += self.patients.medical_charge
            self.assertEqual(total, 5000)
        elif self.patients.medical_charge and self.patients.patient.consultation:
            amount_charged = self.patients.medical_charge \
                + self.patients.patient.consultation
            total += amount_charged
            self.assertEqual(total, 6000)
            
 
        

    def test_patients_user_profile(self):
        """ function that assert follow up plan user profile username """
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(userprofile.user.username, "Bruno")

    def test_patients_user_organization(self):
        """ function that assert follow up plan  organization is same with the  userprofile
        during post_save signal instance."""
        userprofile, created = UserProfile.objects.get_or_create(
            user=self.user)
        self.assertEqual(self.patients.organization, userprofile)

    def test_patients_user(self):
        """ function that assert follow up plan  organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.patients.user, self.user)

    def test_patients_patient_name(self):
        """ function that assert follow up plan  organization is same with the  userprofile
        during post_save signal instance."""

        self.assertEqual(self.patients.patient.first_name,
                         self.patient_detail.first_name)
