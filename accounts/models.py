from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    @property
    def is_student(self):
        return self.role == 'student'
        
    @property
    def is_teacher(self):
        return self.role == 'teacher'
        
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def has_completed_profile(self):
        if self.is_admin:
            return True
        if self.role == 'student':
            return hasattr(self, 'student_profile')
        if self.role == 'teacher':
            return hasattr(self, 'teacher_profile')
        return False

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
