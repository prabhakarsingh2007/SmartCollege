from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import User
from courses.models import Department, Subject
from students.models import Student
from chatbot.models import ChatHistory
from chatbot.services import get_chatbot_response

# Python 3.14 compatibility monkey-patch for Django Test Client
from django.template.context import Context, RequestContext
def patch_context_copy(self):
    duplicate = Context()
    duplicate.dicts = self.dicts[:]
    return duplicate
Context.__copy__ = patch_context_copy
RequestContext.__copy__ = patch_context_copy

class ChatbotTestCase(TestCase):
    def setUp(self):
        # Create department
        self.dept = Department.objects.create(name='Electronics', code='ECE')
        
        # Create user
        self.student_user = User.objects.create_user(
            username='chatstudent1', password='securepassword123', role='student'
        )
        
        # Create student profile
        self.student_profile = Student.objects.create(
            user=self.student_user,
            roll_no='S2002',
            registration_no='REG2002',
            department=self.dept,
            semester=3,
            phone='9876543212'
        )

    def test_chatbot_fallback_mock_response(self):
        # Retrieve chatbot response under mock fallback (GEMINI_API_KEY is empty or not set)
        response = get_chatbot_response(self.student_user, "What is my department code?")
        self.assertIn("ECE", response)
        self.assertIn("chatstudent1", response)

    def test_chatbot_view_saves_history(self):
        self.client.login(username='chatstudent1', password='securepassword123')
        
        # Post a question to chatbot view
        response = self.client.post(reverse('chatbot'), {
            'question': 'Tell me about ECE department.'
        })
        # Check redirect to chatbot
        self.assertRedirects(response, reverse('chatbot'))
        
        # Verify ChatHistory record was created in the database
        self.assertTrue(ChatHistory.objects.filter(
            user=self.student_user,
            question='Tell me about ECE department.'
        ).exists())
