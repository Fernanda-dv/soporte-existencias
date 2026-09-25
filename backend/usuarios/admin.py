from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Tecnico

@admin.register(Tecnico)
class TecnicoAdmin(UserAdmin):
    pass