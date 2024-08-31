from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import DefaultAccount


class DefaultAccountAdmin(UserAdmin):
    model = DefaultAccount


admin.site.register(DefaultAccount, DefaultAccountAdmin)
