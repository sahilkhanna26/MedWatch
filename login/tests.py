# tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import CustomUser, Report
from django.test import Client

class CustomUserTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )

    def test_create_user(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_superuser_creation(self):
        superuser = self.User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpassword'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

class ViewsTest(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('login:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_custom_redirect_view(self):
        response = self.client.get(reverse('login:custom_redirect'))
        self.assertEqual(response.status_code, 302)  # Redirect status code

class ReportModelTest(TestCase):
    def setUp(self):
        self.report = Report.objects.create(
            name_reported='Test Report',
            description='This is a test report',
            status='New'
        )

    def test_report_creation(self):
        self.assertEqual(self.report.name_reported, 'Test Report')
        self.assertEqual(self.report.description, 'This is a test report')
        self.assertEqual(self.report.status, 'New')




