from django.db import models


class Activity(models.Model):
    """
    Model to represent an activity within a project in the project management system. It includes fields for
    description, associated project, priority, status, creation date, and expected completion date. This model
    is designed to track detailed tasks and their progress within a project.
    """

    PRIORITY_CHOICES = [("high", "Alta"), ("medium", "Média"), ("low", "Baixa")]
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("in_progress", "Em andamento"),
        ("completed", "Concluída"),
        ("requires_attention", "Requer Atenção"),
        ("blocked", "Bloqueada"),
    ]

    created_by = models.ForeignKey("accounts.DefaultAccount", on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="activities")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    creation_date = models.DateField(auto_now_add=True)
    expected_completion_date = models.DateField()

    def __str__(self):
        return self.description
