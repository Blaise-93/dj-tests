from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from songs.models import User
from django.shortcuts import redirect, render
from utils import (
    slug_modifier,
    generate_patient_unique_code,
    date_signed_in_and_or_out,
    time_in_hr_min

)
from django.urls import reverse
from staff.models import *
from leads.models import *


# Attendance

class AttendanceTestView(TestCase):
    """ Unit tests for the Attendance of our model """

    def setUp(self):
        ''' set up non-modified attendance object used by
         by all class method: this action is performed once '''

        # super(AttendanceTestView, self).setUpClass()

        time = timezone.now() - timedelta(hours=1)

        self.user = User.objects.create(
            username='Chinwe',
            first_name='Chinwe',
            last_name='Okeke',
            email='test_email',
            password='chinwe##'
        )

        self.profile_user, created = UserProfile.objects.get_or_create(
            user=self.user)

        self.management = Management.objects.create(
            user=self.user,
            first_name='Uche',
            last_name="Egini",
            phone_number='080345476532',
            email='ucheegini@gmail.com',
            slug=slug_modifier(),
            organization=self.profile_user,
            date_joined=time,

        )

        self.attendance1 = Attendance.objects.create(
            full_name='John Okafor',
            organization=self.profile_user,
            management=self.management,
            slug=slug_modifier(),
            date_created=time,
            user=self.user,
            sign_in_time='8:00',
            staff_attendance_ref=generate_patient_unique_code(),
            sign_out_time=time_in_hr_min(),
            date_sign_out_time=date_signed_in_and_or_out(),

        )

        self.attendance2 = Attendance.objects.create(
            full_name='Onyekwelu',
            organization=self.profile_user,
            management=self.management,
            slug=slug_modifier(),
            user=self.user,
            date_created=time,
            sign_in_time='8:00',
            staff_attendance_ref=generate_patient_unique_code(),
            sign_out_time=time_in_hr_min(),
            date_sign_out_time=date_signed_in_and_or_out(),
        )

        self.attendance_page_response = self.client.get(
            reverse('staff:attendance'))

        self.attendance1_detail_page_response = self.client.\
            get(self.attendance1.get_absolute_url())

        # attendance 2 - get it's detail view
        self.attendance2_detail_page_response = self.client\
        .get(self.attendance2.get_absolute_url())

        # login the user to our page
        self.login = self.client.login(
            username="test_user", password="testcase##")

        # create attendance
        self.create_attendance = self.client.post(reverse('staff:attendance'), data={
            'full_name': "full name",
            'sign_in_time': time_in_hr_min(),
            'sign_out_time': '2:40'

        })

        self.response = self.client.get(reverse('landing-page'))

    # python manage.py test staff.tests.test_views.test_attendance
    # <HttpResponseRedirect status_code=302, "text/html; charset=utf-8", url="/">

    def test_attendance1_contains_correct_context(self):
        """ test and assert that attendance page contains correct context """
        
        self.assertIn("request", self.attendance_page_response.context)
        
    def test_attendance_page_contains_correct_302_status_code(self):
        """ test and assert that attendance page contains correct 302 status code
        for redirect"""
        
        print(self.attendance1_detail_page_response)
        print(self.attendance_page_response)
        self.assertEqual(self.attendance1_detail_page_response.status_code, 302)
        self.assertEqual(self.attendance1_detail_page_response.context, self.attendance1)
        
        
        #self.assertContains(self.attendance1_detail_page_response, self.attendance1.full_name )
        #self.assertContains(self.attendance1_detail_page_response, self.attendance1.organization )
        #self.assertContains(self.attendance1_detail_page_response, self.attendance1.sign_in_time )
