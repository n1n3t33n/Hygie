from rest_framework import generics, permissions

from apps.comptes.permissions import PeutCreerAdministrateur, PeutGererUtilisateurs
from apps.comptes.serializers.gestion_utilisateurs import (
    AdministrateurCreationSerializer,
    AgentCreationSerializer,
)


class AgentCreationView(generics.CreateAPIView):
    """POST /api/comptes/gestion-utilisateurs/agents/"""
    serializer_class = AgentCreationSerializer
    permission_classes = [permissions.IsAuthenticated, PeutGererUtilisateurs]


class AdministrateurCreationView(generics.CreateAPIView):
    """POST /api/comptes/gestion-utilisateurs/administrateurs/"""
    serializer_class = AdministrateurCreationSerializer
    permission_classes = [permissions.IsAuthenticated, PeutCreerAdministrateur]