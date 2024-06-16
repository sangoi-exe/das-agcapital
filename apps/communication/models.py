from django.core.validators import RegexValidator
from django.db import models

from apps.accounts.models import CustomUser


class Message(models.Model):
    """
    Model to represent a message between users in the system. It includes sender, receiver, content, and timestamp.
    """

    sender = models.ForeignKey("accounts.CustomUser", related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        "accounts.CustomUser",
        related_name="received_messages",
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"
