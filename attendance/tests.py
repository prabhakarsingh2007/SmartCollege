from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from courses.models import Department, Subject
from students.models import Student
from teachers.models import Teacher
from attendance.models import QRSession, Attendance
from attendance.views import calculate_distance

# Python 3.14 compatibility monkey-patch for Django Test Client
from django.template.context import Context, RequestContext
def patch_context_copy(self):
    duplicate = Context()
    duplicate.dicts = self.dicts[:]
    return duplicate
Context.__copy__ = patch_context_copy
RequestContext.__copy__ = patch_context_copy

class AttendanceGeofencingTestCase(TestCase):
    def setUp(self):
        # Create department
        self.dept = Department.objects.create(name='Computer Science', code='CSE')
        
        # Create users
        self.teacher_user = User.objects.create_user(
            username='prof1', password='securepassword123', role='teacher'
        )
        self.student_user = User.objects.create_user(
            username='stud1', password='securepassword123', role='student'
        )
        
        # Create profiles
        self.teacher_profile = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T1001',
            department=self.dept,
            designation='Assistant Professor',
            phone='9876543210'
        )
        self.student_profile = Student.objects.create(
            user=self.student_user,
            roll_no='S2001',
            registration_no='REG2001',
            department=self.dept,
            semester=3,
            phone='9876543211'
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Algorithms',
            code='CSE-301',
            department=self.dept,
            semester=3,
            teacher=self.teacher_profile
        )

    def test_calculate_distance(self):
        # Points very close (within ~1m)
        dist = calculate_distance(12.971598, 77.594562, 12.971590, 77.594560)
        self.assertLess(dist, 5.0)
        
        # Points far away (Bangalore to Chennai ~290km)
        dist_far = calculate_distance(12.971598, 77.594562, 13.082680, 80.270718)
        self.assertGreater(dist_far, 200000.0)

    def test_refresh_qr_session_api(self):
        # Create session
        session = QRSession.objects.create(
            subject=self.subject,
            teacher=self.teacher_profile,
            latitude=12.971598,
            longitude=77.594562,
            expires_at=timezone.now() + timezone.timedelta(seconds=20)
        )
        original_token = session.token
        
        # Log in teacher
        self.client.login(username='prof1', password='securepassword123')
        
        # Call refresh URL
        response = self.client.get(reverse('refresh_qr_session', args=[session.id]))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertNotEqual(data['token'], original_token.hex)
        self.assertIn('qr_base64', data)
        
        # Verify in DB
        session.refresh_from_db()
        self.assertNotEqual(session.token, original_token)

    def test_student_scan_geofencing_success(self):
        # Create session
        session = QRSession.objects.create(
            subject=self.subject,
            teacher=self.teacher_profile,
            latitude=12.971598,
            longitude=77.594562,
            expires_at=timezone.now() + timezone.timedelta(seconds=20)
        )
        
        self.client.login(username='stud1', password='securepassword123')
        
        # Submit within 50m (difference ~1 meter)
        response = self.client.post(reverse('scan_qr_attendance'), {
            'qr_token': str(session.token),
            'latitude': '12.971598',
            'longitude': '77.594562'
        })
        self.assertRedirects(response, reverse('student_attendance'))
        
        # Verify attendance marked
        self.assertTrue(Attendance.objects.filter(
            student=self.student_profile,
            subject=self.subject,
            status='Present'
        ).exists())

    def test_student_scan_geofencing_failure_far_away(self):
        # Create session
        session = QRSession.objects.create(
            subject=self.subject,
            teacher=self.teacher_profile,
            latitude=12.971598,
            longitude=77.594562,
            expires_at=timezone.now() + timezone.timedelta(seconds=20)
        )
        
        self.client.login(username='stud1', password='securepassword123')
        
        # Submit far away (Bangalore to Chennai)
        response = self.client.post(reverse('scan_qr_attendance'), {
            'qr_token': str(session.token),
            'latitude': '13.082680',
            'longitude': '80.270718'
        })
        self.assertRedirects(response, reverse('scan_qr_attendance'))
        
        # Verify no attendance marked
        self.assertFalse(Attendance.objects.filter(
            student=self.student_profile,
            subject=self.subject
        ).exists())
