from rest_framework import serializers

from apps.reservations.models import Vehicule
from apps.reservations.services import vehicules as service_vehicules
from apps.reservations.services.exceptions import ErreurMetier


def _en_erreur_de_validation(erreur):
    """Traduit une ErreurMetier du service en erreur 400 DRF, rattachée à son champ."""
    if erreur.champ:
        return serializers.ValidationError({erreur.champ: [erreur.message]})
    return serializers.ValidationError(erreur.message)


class VehiculeSerializer(serializers.ModelSerializer):
    """
    Véhicule d'un Client (P1, messages 5-8 : ajouterVehicule(immatriculation, typeVehicule)).

    Le client n'est jamais lu dans le corps de la requête : il est imposé par la vue à partir
    de l'utilisateur authentifié. Aucune règle métier ici — elles vivent dans
    services/vehicules.py.
    """
    # Limite large côté API : l'immatriculation est normalisée (espaces supprimés) puis
    # contrôlée contre la limite réelle de 20 caractères par le service.
    immatriculation = serializers.CharField(max_length=50)

    class Meta:
        model = Vehicule
        fields = ['id_vehicule', 'immatriculation', 'type_vehicule', 'client']
        read_only_fields = ['id_vehicule', 'client']
        # L'unicité (client, immatriculation) est portée par le service et la contrainte en base.
        validators = []

    def validate_immatriculation(self, valeur):
        try:
            return service_vehicules.valider_immatriculation(valeur)
        except ErreurMetier as erreur:
            raise _en_erreur_de_validation(erreur)

    def create(self, validated_data):
        try:
            return service_vehicules.creer_vehicule(**validated_data)
        except ErreurMetier as erreur:
            raise _en_erreur_de_validation(erreur)

    def update(self, instance, validated_data):
        try:
            return service_vehicules.modifier_vehicule(instance, **validated_data)
        except ErreurMetier as erreur:
            raise _en_erreur_de_validation(erreur)