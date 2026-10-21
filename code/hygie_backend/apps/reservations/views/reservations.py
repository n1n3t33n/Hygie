from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.reservations.api_erreurs import ConflitMetier
from apps.reservations.models import Reservation, StatutReservation
from apps.reservations.permissions import PeutGererReservations
from apps.reservations.serializers.reservations import ReservationSerializer
from apps.reservations.services import reservations as service_reservations
from apps.reservations.services.exceptions import ErreurMetier


class PaginationReservations(PageNumberPagination):
    """Pagination propre à la liste des réservations (aucune pagination globale)."""
    page_size = 20


class _ReservationBaseView:
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, PeutGererReservations]

    def get_queryset(self):
        # drf-spectacular génère le schéma Swagger sans utilisateur réel.
        if getattr(self, 'swagger_fake_view', False):
            return Reservation.objects.none()
        return service_reservations.reservations_accessibles(self.request.user)


class ReservationListCreateView(_ReservationBaseView, generics.ListCreateAPIView):
    """
    GET  /api/reservations/reservations/ — mes réservations (Client) ou toutes (Administrateur
                                           habilité), 20 par page, filtre facultatif ?statut=
    POST /api/reservations/reservations/ — réserver (Client uniquement), toujours « en attente »
    """
    pagination_class = PaginationReservations

    @property
    def action_reservation(self):
        return 'creer' if self.request.method == 'POST' else 'consulter'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method != 'GET':
            return queryset
        statut = self.request.query_params.get('statut')
        if statut:
            if statut not in StatutReservation.values:
                raise ValidationError({
                    'statut': [f"Valeur invalide. Valeurs possibles : {', '.join(StatutReservation.values)}."]
                })
            queryset = queryset.filter(statut=statut)
        return queryset.order_by('-date_reservation', 'creneau', 'id_reservation')

    def perform_create(self, serializer):
        # Le client vient du jeton d'authentification, jamais du corps de la requête.
        serializer.save(client=self.request.user.client)


class ReservationDetailView(_ReservationBaseView, generics.RetrieveAPIView):
    """
    GET /api/reservations/reservations/<pk>/
    Une réservation d'un autre client répond 404 (son existence n'est pas révélée).
    """
    action_reservation = 'consulter'


class _ReservationActionView(_ReservationBaseView, generics.GenericAPIView):
    """Transition d'état : POST sans corps. Refus d'état ou de délai -> 409."""
    http_method_names = ['post', 'options']

    def executer(self, reservation):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        reservation = self.get_object()
        try:
            self.executer(reservation)
        except ErreurMetier as erreur:
            raise ConflitMetier(erreur.message)
        return Response(self.get_serializer(reservation).data)


class ReservationAnnulerView(_ReservationActionView):
    """POST /api/reservations/reservations/<pk>/annuler/ — Client (jusqu'à la veille) ou Administrateur."""
    action_reservation = 'annuler'

    def executer(self, reservation):
        service_reservations.annuler_reservation(
            reservation, acteur_est_admin=self.request.user.get_role() == 'administrateur',
        )


class ReservationConfirmerView(_ReservationActionView):
    """POST /api/reservations/reservations/<pk>/confirmer/ — Administrateur habilité."""
    action_reservation = 'administrer'

    def executer(self, reservation):
        service_reservations.confirmer_reservation(reservation)


class ReservationTerminerView(_ReservationActionView):
    """POST /api/reservations/reservations/<pk>/terminer/ — Administrateur habilité, dès le jour prévu."""
    action_reservation = 'administrer'

    def executer(self, reservation):
        service_reservations.terminer_reservation(reservation)