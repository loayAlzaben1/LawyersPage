from django.test import TestCase
from django.urls import reverse


class CoreViewsTests(TestCase):
    def test_home_status_code(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)

    def test_about_status_code(self):
        resp = self.client.get(reverse('core:about'))
        self.assertEqual(resp.status_code, 200)

    def test_services_status_code(self):
        resp = self.client.get(reverse('core:services'))
        self.assertEqual(resp.status_code, 200)

    def test_faq_status_code(self):
        resp = self.client.get(reverse('core:faq'))
        self.assertEqual(resp.status_code, 200)

    def test_contact_status_code(self):
        resp = self.client.get(reverse('core:contact'))
        self.assertEqual(resp.status_code, 200)

    def test_appointment_status_code(self):
        resp = self.client.get(reverse('core:appointment'))
        self.assertEqual(resp.status_code, 200)
