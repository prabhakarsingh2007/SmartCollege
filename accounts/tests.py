from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Python 3.14 compatibility monkey-patch for Django Test Client
from django.template.context import Context, RequestContext
def patch_context_copy(self):
    duplicate = Context()
    duplicate.dicts = self.dicts[:]
    return duplicate
Context.__copy__ = patch_context_copy
RequestContext.__copy__ = patch_context_copy

User = get_user_model()

class AccountsTestCase(TestCase):
    def setUp(self):
        # Create standard test users
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@college.edu',
            password='testpassword123',
            role='student'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@college.edu',
            password='testpassword123',
            role='teacher'
        )
        self.admin_user = User.objects.create_user(
            username='admin1',
            email='admin1@college.edu',
            password='testpassword123',
            role='admin',
            is_staff=True
        )

    def test_user_creation_roles(self):
        """Verify that user role properties work correctly."""
        self.assertTrue(self.student_user.is_student)
        self.assertFalse(self.student_user.is_teacher)
        self.assertFalse(self.student_user.is_admin)

        self.assertTrue(self.teacher_user.is_teacher)
        self.assertFalse(self.teacher_user.is_student)
        self.assertFalse(self.teacher_user.is_admin)

        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.admin_user.is_student)
        self.assertFalse(self.admin_user.is_teacher)

    def test_login_url_resolves(self):
        """Verify the login URL resolves and returns 200 OK."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_url_resolves(self):
        """Verify the registration URL resolves and returns 200 OK."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_anonymous(self):
        """Verify dashboard redirects anonymous user to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
