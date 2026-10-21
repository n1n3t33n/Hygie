from django.urls import path

from apps.reservations.views.abonnements import AbonnementDetailView, AbonnementListCreateView
from apps.reservations.views.reservations import (
    ReservationAnnulerView,
    ReservationConfirmerView,
    ReservationDetailView,
    ReservationListCreateView,
    ReservationTerminerView,
)
from apps.reservations.views.vehicules import VehiculeDetailView, VehiculeListCreateView

app_name = 'reservations'

urlpatterns = [
    path('vehicules/', VehiculeListCreateView.as_view(), name='vehicule-list-create'),
    path('vehicules/<int:pk>/', VehiculeDetailView.as_view(), name='vehicule-detail'),
    path('abonnements/', AbonnementListCreateView.as_view(), name='abonnement-list-create'),
    path('abonnements/<int:pk>/', AbonnementDetailView.as_view(), name='abonnement-detail'),
    path('reservations/', ReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/annuler/', ReservationAnnulerView.as_view(), name='reservation-annuler'),
    path('reservations/<int:pk>/confirmer/', ReservationConfirmerView.as_view(), name='reservation-confirmer'),
    path('reservations/<int:pk>/terminer/', ReservationTerminerView.as_view(), name='reservation-terminer'),
]