from django.db import models
from django.conf import settings

class ChatHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_histories')
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Chat Histories"
        ordering = ['timestamp']

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
