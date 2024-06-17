# Generated by Django 5.0.6 on 2024-06-17 02:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("projects", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("high", "Alta"),
                            ("medium", "Média"),
                            ("low", "Baixa"),
                        ],
                        default="medium",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("in_progress", "Em andamento"),
                            ("completed", "Concluída"),
                            ("requires_attention", "Requer Atenção"),
                            ("blocked", "Bloqueada"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("creation_date", models.DateField(auto_now_add=True)),
                ("expected_completion_date", models.DateField()),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="projects.project",
                    ),
                ),
            ],
        ),
    ]
