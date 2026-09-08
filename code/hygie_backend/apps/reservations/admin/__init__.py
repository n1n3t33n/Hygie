from django.contrib import admin

from apps.reservations.models import Abonnement, Reservation, Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'client')
    list_filter = ('type_vehicule',)
    search_fields = ('immatriculation', 'client__utilisateur__username')


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('client', 'frequence', 'date_debut', 'date_fin')
    list_filter = ('frequence',)
    search_fields = ('client__utilisateur__username',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id_reservation', 'client', 'date_reservation', 'creneau', 'statut')
    list_filter = ('statut', 'creneau')
    search_fields = ('client__utilisateur__username',)
    date_hierarchy = 'date_reservation'