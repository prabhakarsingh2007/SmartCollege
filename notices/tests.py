from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import User
from notices.models import Notice

# Python 3.14 compatibility monkey-patch for Django Test Client
from django.template.context import Context, RequestContext
def patch_context_copy(self):
    duplicate = Context()
    duplicate.dicts = self.dicts[:]
    return duplicate
Context.__copy__ = patch_context_copy
RequestContext.__copy__ = patch_context_copy

class NoticesTestCase(TestCase):
    def setUp(self):
        from courses.models import Department
        from teachers.models import Teacher
        
        # Create standard test user
        self.user = User.objects.create_user(
            username='noticetest1',
            email='noticetest1@college.edu',
            password='testpassword123',
            role='teacher'
        )
        self.dept = Department.objects.create(name='Computer Science', code='CSE')
        self.teacher_profile = Teacher.objects.create(
            user=self.user,
            employee_id='T1002',
            department=self.dept,
            designation='Lecturer',
            phone='9876543210'
        )

    def test_anonymous_latest_notice_redirects_to_login(self):
        response = self.client.get(reverse('latest_notice_api'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_latest_notice_empty(self):
        self.client.login(username='noticetest1', password='testpassword123')
        response = self.client.get(reverse('latest_notice_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'empty')

    def test_latest_notice_success(self):
        self.client.login(username='noticetest1', password='testpassword123')
        
        # Create a test notice
        Notice.objects.create(
            title='Class Cancelled',
            description='The DSA class tomorrow is cancelled.',
            created_by=self.user
        )
        
        response = self.client.get(reverse('latest_notice_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['title'], 'Class Cancelled')
        self.assertIn('The DSA class', data['description'])
        self.assertEqual(data['created_by'], 'noticetest1')
