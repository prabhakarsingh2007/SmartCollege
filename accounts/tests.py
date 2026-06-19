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

    def test_authenticated_user_without_profile_redirects_to_complete_profile(self):
        """Verify that an authenticated student without a profile is redirected to complete_profile."""
        self.client.login(username='student1', password='testpassword123')
        
        # Accessing dashboard should redirect to complete_profile
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('complete_profile'))

        # Accessing timetable should redirect to complete_profile
        response = self.client.get(reverse('timetable_view'))
        self.assertRedirects(response, reverse('complete_profile'))

    def test_authenticated_user_with_profile_can_access_dashboard(self):
        """Verify that an authenticated student with a profile can access the dashboard."""
        from courses.models import Department
        from students.models import Student
        
        # Create department and profile
        dept = Department.objects.create(name='Computer Science', code='CSE')
        Student.objects.create(
            user=self.student_user,
            roll_no='12345',
            registration_no='REG12345',
            department=dept,
            semester=3,
            phone='1234567890'
        )
        
        self.client.login(username='student1', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('subject_names', response.context)
        self.assertIn('subject_pcts', response.context)

    def test_non_admin_cannot_access_custom_admin_panel(self):
        """Verify that a student user is blocked from the custom admin panel."""
        from courses.models import Department
        from students.models import Student
        dept = Department.objects.create(name='Computer Science', code='CSE')
        Student.objects.create(
            user=self.student_user,
            roll_no='12345',
            registration_no='REG12345',
            department=dept,
            semester=3,
            phone='1234567890'
        )
        self.client.login(username='student1', password='testpassword123')
        response = self.client.get(reverse('custom_admin_panel'))
        # Should redirect to dashboard
        self.assertRedirects(response, reverse('dashboard'))

    def test_admin_can_access_custom_admin_panel(self):
        """Verify that an administrator can load the custom admin panel."""
        self.client.login(username='admin1', password='testpassword123')
        response = self.client.get(reverse('custom_admin_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('active_tab', response.context)

    def test_admin_can_create_department_via_post(self):
        """Verify that an admin can create a department via the panel POST request."""
        from courses.models import Department
        self.client.login(username='admin1', password='testpassword123')
        
        response = self.client.post(reverse('custom_admin_panel') + "?tab=departments", {
            'action': 'add_department',
            'name': 'Civil Engineering',
            'code': 'CIVIL'
        })
        # Should redirect back to admin-panel?tab=departments
        self.assertRedirects(response, reverse('custom_admin_panel') + "?tab=departments")
        
        # Verify in DB
        self.assertTrue(Department.objects.filter(code='CIVIL', name='Civil Engineering').exists())
