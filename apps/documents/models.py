from django.db import models
from apps.projects.models import Project
from django.core.validators import RegexValidator
from django.core.files.storage import FileSystemStorage

class Document(models.Model):
    """
    Model to represent a document associated with a project. It includes fields for document name, file upload, 
    and project association.
    """
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey('projects.Project', related_name='documents', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
