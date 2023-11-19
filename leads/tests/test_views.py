from django.test import TestCase
from leads.views import LandingPageView
from django.urls import reverse


class LandingPageTest(TestCase):
    pass

    def test_get(self):

        response = self.client.get(reverse('landing-page'))
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leads/landing-page.html')
        response = self.client.get(reverse('landing-page'))
        # TODO some sort of test
        self.assertTemplateUsed(response, 'leads/landing-page.html')
 
