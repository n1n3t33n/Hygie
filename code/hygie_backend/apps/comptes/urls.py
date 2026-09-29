from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.comptes.views.gestion_utilisateurs import AdministrateurCreationView, AgentCreationView
from apps.comptes.views.inscription import ClientInscriptionView

app_name = 'comptes'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('inscription/', ClientInscriptionView.as_view(), name='client-inscription'),
    path('gestion-utilisateurs/agents/', AgentCreationView.as_view(), name='agent-creation'),
    path('gestion-utilisateurs/administrateurs/', AdministrateurCreationView.as_view(), name='administrateur-creation'),
]