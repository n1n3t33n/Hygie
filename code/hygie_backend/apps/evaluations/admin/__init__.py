from django.contrib import admin

from apps.evaluations.models import Avis, Signalement


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id_avis', 'mission', 'note')
    list_filter = ('note',)
    search_fields = ('mission__reservation__client__utilisateur__username',)


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ('id_signalement', 'mission', 'type_signalement')
    list_filter = ('type_signalement',)
    search_fields = ('mission__reservation__client__utilisateur__username', 'description')