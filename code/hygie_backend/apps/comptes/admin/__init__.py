from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.comptes.models import Agent, Client, Utilisateur, Zone

admin.site.register(Utilisateur, UserAdmin)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_zone')
    list_filter = ('type_zone',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'telephone', 'zone', 'point_eau_disponible')
    list_filter = ('zone', 'point_eau_disponible')
    search_fields = ('utilisateur__username', 'telephone')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'telephone', 'role')
    list_filter = ('role',)
    search_fields = ('utilisateur__username', 'telephone')