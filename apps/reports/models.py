from django.db import models

from apps.projects.models import Project
from apps.cleitons.models import Cleiton


class Report(models.Model):
    """
    Model to represent a report related to a project. It includes fields for title, content, generation time,
    and project association.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reports")
    cleiton = models.ForeignKey(Cleiton, on_delete=models.CASCADE, related_name="reports")

    def __str__(self):
        return self.title
