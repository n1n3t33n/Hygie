from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.comptes.views.gestion_utilisateurs import (
    AdministrateurDesactivationView, AdministrateurDetailView, AdministrateurListCreateView,
    AgentDesactivationView, AgentDetailView, AgentListCreateView,
    ClientDesactivationView, ClientDetailView, ClientListView,
)
from apps.comptes.views.inscription import ClientInscriptionView

app_name = 'comptes'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('inscription/', ClientInscriptionView.as_view(), name='client-inscription'),

    path('gestion-utilisateurs/agents/', AgentListCreateView.as_view(), name='agent-list-create'),
    path('gestion-utilisateurs/agents/<int:pk>/', AgentDetailView.as_view(), name='agent-detail'),
    path('gestion-utilisateurs/agents/<int:pk>/desactiver/', AgentDesactivationView.as_view(), name='agent-desactiver'),

    path('gestion-utilisateurs/clients/', ClientListView.as_view(), name='client-list'),
    path('gestion-utilisateurs/clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('gestion-utilisateurs/clients/<int:pk>/desactiver/', ClientDesactivationView.as_view(), name='client-desactiver'),

    path('gestion-utilisateurs/administrateurs/', AdministrateurListCreateView.as_view(), name='administrateur-list-create'),
    path('gestion-utilisateurs/administrateurs/<int:pk>/', AdministrateurDetailView.as_view(), name='administrateur-detail'),
    path('gestion-utilisateurs/administrateurs/<int:pk>/desactiver/', AdministrateurDesactivationView.as_view(), name='administrateur-desactiver'),
]