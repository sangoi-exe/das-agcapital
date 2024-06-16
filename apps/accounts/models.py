from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    """
    Model to represent a user in the system. Includes custom fields for CPF and mobile phone number,
    with validation for Brazilian standards.
    """
    cpf_validator = RegexValidator(r'^\d{11}$', 'CPF deve conter 11 dígitos, apenas números.')
    phone_validator = RegexValidator(r'^\d{11}$', 'O número de telefone deve seguir o formato XX9XXXXXXX.')

    cpf = models.CharField('CPF', max_length=11, unique=True, validators=[cpf_validator])
    phone_number = models.CharField('Número de Celular', max_length=11, validators=[phone_validator], blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",
        related_query_name="customuser",
    )

    def __str__(self):
        return self.username
    

