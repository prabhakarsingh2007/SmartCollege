from django.db import models

class Notes(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, related_name='notes')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='notes')
    file = models.FileField(upload_to='notes/')
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notes"

    def __str__(self):
        return f"{self.title} ({self.subject.name})"
