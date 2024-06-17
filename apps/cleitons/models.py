from django.db import models
from django.contrib.auth import get_user_model


class Cleiton(models.Model):
    """
    Model to represent a client in the project management system.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
