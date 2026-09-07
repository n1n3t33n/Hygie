from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.comptes.models import Utilisateur

admin.site.register(Utilisateur, UserAdmin)