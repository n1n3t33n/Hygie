from rest_framework import generics, permissions

from apps.reservations.api_erreurs import ConflitMetier
from apps.reservations.models import Vehicule
from apps.reservations.permissions import PeutGererVehicules
from apps.reservations.serializers.vehicules import VehiculeSerializer
from apps.reservations.services import vehicules as service_vehicules
from apps.reservations.services.exceptions import ErreurMetier


class _VehiculeBaseView:
    serializer_class = VehiculeSerializer
    permission_classes = [permissions.IsAuthenticated, PeutGererVehicules]

    def get_queryset(self):
        # drf-spectacular génère le schéma Swagger sans utilisateur réel.
        if getattr(self, 'swagger_fake_view', False):
            return Vehicule.objects.none()
        return service_vehicules.vehicules_accessibles(self.request.user).order_by(
            'immatriculation', 'id_vehicule'
        )


class VehiculeListCreateView(_VehiculeBaseView, generics.ListCreateAPIView):
    """
    GET  /api/reservations/vehicules/ — mes véhicules (Client) ou tous (Administrateur habilité)
    POST /api/reservations/vehicules/ — ajouter un véhicule (Client uniquement)
    """

    def perform_create(self, serializer):
        # Le client vient du jeton d'authentification, jamais du corps de la requête.
        serializer.save(client=self.request.user.client)


class VehiculeDetailView(_VehiculeBaseView, generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/reservations/vehicules/<pk>/
    Un véhicule d'un autre client répond 404 (son existence n'est pas révélée).
    """

    def perform_destroy(self, instance):
        try:
            service_vehicules.supprimer_vehicule(instance)
        except ErreurMetier as erreur:
            raise ConflitMetier(erreur.message)