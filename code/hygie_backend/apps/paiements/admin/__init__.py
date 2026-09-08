from django.contrib import admin

from apps.paiements.models import Paiement, Tarif


@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom',)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id_paiement', 'reservation', 'montant', 'mode_paiement', 'date_paiement')
    list_filter = ('mode_paiement',)
    search_fields = ('reservation__client__utilisateur__username',)
    date_hierarchy = 'date_paiement'