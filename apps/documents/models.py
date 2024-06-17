from django.db import models
from django.core.validators import RegexValidator
from django.core.files.storage import FileSystemStorage

from apps.projects.models import Project


class Document(models.Model):
    """
    Model to represent a document associated with a project. It includes fields for document name, file upload,
    and project association.
    """

    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    file = models.CharField(max_length=255)  # simular o envio de um arquivo
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
