from django.db import models
from apps.activities.models import Activity
from apps.cleitons.models import Cleiton
from apps.documents.models import Document
from apps.projects.models import Project
from apps.reports.models import Report
from apps.tasks.models import Task


class Notification(models.Model):
    """
    Model to represent a notification to be sent to a user. It includes recipient, title, message, and timestamps
    for creation and reading.
    """

    cleiton = models.ForeignKey(Cleiton, on_delete=models.CASCADE, related_name="notifications")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")

    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
