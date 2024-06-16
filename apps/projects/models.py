from django.core.validators import RegexValidator
from django.db import models

from apps.cleitons.models import Cleiton


class Project(models.Model):
    """
    Model to represent a project in the project management system. It includes fields for the project's name,
    description, associated client, status, start date, and estimated end date. The status field allows tracking
    the project's progress through various states like open, in progress, and completed.
    """

    STATUS_CHOICES = [
        ("open", "Aberto"),
        ("in_progress", "Em andamento"),
        ("completed", "Concluído"),
        ("requires_attention", "Requer Atenção"),
        ("on_hold", "Em Espera"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    cleiton = models.ForeignKey("cleitons.Cleiton", on_delete=models.CASCADE, related_name="projects")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    start_date = models.DateField()
    estimated_end_date = models.DateField()

    def __str__(self):
        return self.name
