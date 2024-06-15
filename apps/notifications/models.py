from django.db import models
from apps.accounts.models import CustomUser
from django.core.validators import RegexValidator

class Notification(models.Model):
    """
    Model to represent a notification to be sent to a user. It includes recipient, title, message, and timestamps
    for creation and reading.
    """
    recipient = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
