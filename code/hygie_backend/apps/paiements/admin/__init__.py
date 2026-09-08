from django.contrib import admin

from apps.paiements.models import Tarif


@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom',)