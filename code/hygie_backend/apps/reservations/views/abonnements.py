from rest_framework import generics, permissions
from rest_framework.response import Response

from apps.reservations.api_erreurs import ConfirmationRequise
from apps.reservations.models import Abonnement
from apps.reservations.permissions import PeutGererAbonnements
from apps.reservations.serializers.abonnements import (
    AbonnementFinSerializer,
    AbonnementSerializer,
)
from apps.reservations.services import abonnements as service_abonnements


class _AbonnementBaseView:
    permission_classes = [permissions.IsAuthenticated, PeutGererAbonnements]

    def get_queryset(self):
        # drf-spectacular génère le schéma Swagger sans utilisateur réel.
        if getattr(self, 'swagger_fake_view', False):
            return Abonnement.objects.none()
        return service_abonnements.abonnements_accessibles(self.request.user).order_by(
            '-date_debut', 'id_abonnement'
        )


class AbonnementListCreateView(_AbonnementBaseView, generics.ListCreateAPIView):
    """
    GET  /api/reservations/abonnements/ — mes abonnements (Client) ou tous (Administrateur habilité)
    POST /api/reservations/abonnements/ — souscrire (Client pour lui-même ; Administrateur habilité
                                          pour un client précisé dans le champ « client »)
    """
    serializer_class = AbonnementSerializer


class AbonnementDetailView(_AbonnementBaseView, generics.RetrieveUpdateAPIView):
    """
    GET   /api/reservations/abonnements/<pk>/ — détail
    PATCH /api/reservations/abonnements/<pk>/ — mettre fin à l'abonnement (date_fin uniquement) ;
          si des réservations dépassent la nouvelle fin : 409 « confirmation_requise », puis le
          demandeur renvoie la requête avec annuler_reservations true ou false

    Pas de PUT (inutile : un seul champ est modifiable) ni de DELETE (on met fin à un
    abonnement, on ne l'efface pas). Un abonnement d'un autre client répond 404.
    """
    serializer_class = AbonnementFinSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ConfirmationRequise as question:
            # 409 : des réservations seraient annulées, on attend la réponse du demandeur.
            return Response(question.payload, status=question.status_code)