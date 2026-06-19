from django.db import models
import uuid

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.roll_no} - {self.subject.name} - {self.date}: {self.status}"

class QRSession(models.Model):
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, related_name='qr_sessions')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='qr_sessions')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"QR for {self.subject.name} (Active: {self.is_active})"
