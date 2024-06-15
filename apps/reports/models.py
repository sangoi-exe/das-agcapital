from django.db import models
from apps.projects.models import Project
from django.core.validators import RegexValidator

class Report(models.Model):
    """
    Model to represent a report related to a project. It includes fields for title, content, generation time,
    and project association.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey('projects.Project', related_name='reports', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
