from django.core.validators import RegexValidator
from django.db import models

from apps.activities.models import Activity
from apps.projects.models import Project


class Task(models.Model):
    """
    Model to represent a task within a project or activity. It includes title, description, due date, completion status,
    and associations with projects and activities.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    project = models.ForeignKey("projects.Project", related_name="tasks", on_delete=models.CASCADE)
    activity = models.ForeignKey(
        "activities.Activity",
        related_name="tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title
