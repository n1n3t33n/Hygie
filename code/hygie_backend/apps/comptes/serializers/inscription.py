from django.db import transaction

from rest_framework import serializers

from apps.comptes.models.client import Client
from apps.comptes.serializers.base import CompteMixin


class ClientInscriptionSerializer(CompteMixin, serializers.ModelSerializer):
    """
    Inscription publique d'un Client (cas d'utilisation "S'inscrire", 07 UML).
    Champs alignés sur le message 1 du diagramme de séquence P1 validé :
    sInscrire(nom, prenom, telephone, zoneId, pointEauDisponible).
    """

    class Meta:
        model = Client
        fields = [
            'username', 'password', 'email', 'nom', 'prenom',
            'telephone', 'zone', 'point_eau_disponible',
        ]

    @transaction.atomic
    def create(self, validated_data):
        utilisateur = self._creer_utilisateur(validated_data)
        return Client.objects.create(utilisateur=utilisateur, **validated_data)