# Generated by Django 5.0.6 on 2024-06-17 06:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("cleitons", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Aberto"),
                            ("in_progress", "Em andamento"),
                            ("completed", "Concluído"),
                            ("requires_attention", "Requer Atenção"),
                            ("on_hold", "Em Espera"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("estimated_end_date", models.DateField()),
                (
                    "cleiton",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="cleitons.cleiton",
                    ),
                ),
            ],
        ),
    ]
