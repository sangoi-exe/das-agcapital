from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Event(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    cleiton = models.ForeignKey("cleitons.Cleiton", related_name="events", on_delete=models.CASCADE)
    activity = models.ForeignKey("activities.Activity", related_name="events", on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey("tasks.Task", related_name="events", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


def clean(self):
    if self.end_time < self.start_time:
        raise ValidationError("The end time must be after the start time.")
    if self.start_time < timezone.now():
        raise ValidationError("The start time must not be in the past.")
