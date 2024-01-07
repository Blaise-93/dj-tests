from django.test import TestCase
from leads.views.leads import *
from leads.views.category import *
from django.urls import reverse


class LandingPageTest(TestCase):
    pass

    def test_get(self):

        response = self.client.get(reverse('landing-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leads/landing-page.html')
        response = self.client.get(reverse('landing-page'))
        self.assertTemplateUsed(response, 'leads/landing-page.html')
       # self.assertEqual(self.response.context['WHATSAPP_LINK'], '08099158877')
      #  self.assertIn( "attendance", self.attendance_page_response.context)
        
        
        

     
 
