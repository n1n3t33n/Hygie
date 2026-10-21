from rest_framework import serializers
from rest_framework.settings import api_settings

from apps.reservations.models import Abonnement, Reservation, Vehicule
from apps.reservations.services import abonnements as service_abonnements
from apps.reservations.services import reservations as service_reservations
from apps.reservations.services import vehicules as service_vehicules
from apps.reservations.services.exceptions import ErreurMetier


def _en_erreur_de_validation(erreur):
    """Traduit une ErreurMetier du service en erreur 400 DRF, rattachée à son champ."""
    if erreur.champ:
        return serializers.ValidationError({erreur.champ: [erreur.message]})
    # Même forme de réponse (un dictionnaire) que pour une erreur rattachée à un champ.
    return serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [erreur.message]})


class _VehiculeDuClientField(serializers.PrimaryKeyRelatedField):
    """
    Véhicule choisi parmi ceux de l'appelant. Un véhicule inexistant ou appartenant à un autre
    client donne exactement la même erreur : l'existence des autres n'est pas révélée.
    """

    def get_queryset(self):
        request = self.context.get('request')
        if request is None:  # génération du schéma Swagger
            return Vehicule.objects.none()
        return service_vehicules.vehicules_accessibles(request.user)


class _AbonnementDuClientField(serializers.PrimaryKeyRelatedField):
    """Même principe que pour le véhicule, appliqué aux abonnements."""

    def get_queryset(self):
        request = self.context.get('request')
        if request is None:  # génération du schéma Swagger
            return Abonnement.objects.none()
        return service_abonnements.abonnements_accessibles(request.user)


class ReservationSerializer(serializers.ModelSerializer):
    """
    Lecture et création d'une réservation. Aucune règle métier ici : elles vivent dans
    services/reservations.py.

    Le client est toujours l'utilisateur authentifié (imposé par la vue) et le statut est
    toujours « en attente » à la création : ni l'un ni l'autre ne se lit dans le corps de la
    requête. Le motif d'annulation est en lecture seule. Aucune modification après création
    (on annule puis on recrée).
    """
    vehicule = _VehiculeDuClientField(required=False, allow_null=True)
    abonnement = _AbonnementDuClientField(required=False, allow_null=True)

    class Meta:
        model = Reservation
        fields = [
            'id_reservation', 'client', 'date_reservation', 'creneau',
            'statut', 'motif_annulation', 'vehicule', 'abonnement',
        ]
        read_only_fields = ['id_reservation', 'client', 'statut', 'motif_annulation']
        # L'unicité du créneau est portée par le service et la contrainte en base.
        validators = []

    def create(self, validated_data):
        try:
            return service_reservations.creer_reservation(**validated_data)
        except ErreurMetier as erreur:
            raise _en_erreur_de_validation(erreur)