from django.db import models
from django.conf import settings

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_no = models.CharField(max_length=20, unique=True)
    registration_no = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('courses.Department', on_delete=models.PROTECT, related_name='students')
    semester = models.IntegerField()
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (Roll: {self.roll_no})"
