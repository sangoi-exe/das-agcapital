from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Event(models.Model):
    """
    Model to represent an event in the system's calendar. It includes fields for title, start and end times,
    description, and owner, with validation for start and end times.
    """

    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey("accounts.Account", related_name="events", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_time < self.start_time:
            raise ValidationError("O horário de término deve ser após o horário de início.")
        if self.start_time < timezone.now():
            raise ValidationError("O horário de início não deve ser no passado.")
