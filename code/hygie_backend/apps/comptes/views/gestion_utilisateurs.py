from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.comptes.models.administrateur import Administrateur
from apps.comptes.models.agent import Agent
from apps.comptes.models.client import Client
from apps.comptes.permissions import PeutCreerAdministrateur, PeutModifierModele, PermissionsModeleComplet
from apps.comptes.serializers.gestion_utilisateurs import (
    AdministrateurCreationSerializer, AdministrateurDetailSerializer,
    AgentCreationSerializer, AgentDetailSerializer,
    ClientDetailSerializer,
)


class AgentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/comptes/gestion-utilisateurs/agents/  — liste (capacité view_agent)
    POST /api/comptes/gestion-utilisateurs/agents/  — création (capacité add_agent)
    """
    queryset = Agent.objects.select_related('utilisateur').all()
    permission_classes = [permissions.IsAuthenticated, PermissionsModeleComplet]

    def get_serializer_class(self):
        return AgentCreationSerializer if self.request.method == 'POST' else AgentDetailSerializer


class AgentDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/comptes/gestion-utilisateurs/agents/<pk>/"""
    queryset = Agent.objects.select_related('utilisateur').all()
    serializer_class = AgentDetailSerializer
    permission_classes = [permissions.IsAuthenticated, PermissionsModeleComplet]


class ClientListView(generics.ListAPIView):
    """GET /api/comptes/gestion-utilisateurs/clients/ — liste (capacité view_client)."""
    queryset = Client.objects.select_related('utilisateur', 'zone').all()
    serializer_class = ClientDetailSerializer
    permission_classes = [permissions.IsAuthenticated, PermissionsModeleComplet]


class ClientDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/comptes/gestion-utilisateurs/clients/<pk>/"""
    queryset = Client.objects.select_related('utilisateur', 'zone').all()
    serializer_class = ClientDetailSerializer
    permission_classes = [permissions.IsAuthenticated, PermissionsModeleComplet]


class AdministrateurListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/comptes/gestion-utilisateurs/administrateurs/ — capacité creer_administrateur."""
    queryset = Administrateur.objects.select_related('utilisateur').all()
    permission_classes = [permissions.IsAuthenticated, PeutCreerAdministrateur]

    def get_serializer_class(self):
        return AdministrateurCreationSerializer if self.request.method == 'POST' else AdministrateurDetailSerializer


class AdministrateurDetailView(generics.RetrieveAPIView):
    """GET /api/comptes/gestion-utilisateurs/administrateurs/<pk>/ — lecture seule."""
    queryset = Administrateur.objects.select_related('utilisateur').all()
    serializer_class = AdministrateurDetailSerializer
    permission_classes = [permissions.IsAuthenticated, PeutCreerAdministrateur]


class _DesactivationSerializer(serializers.Serializer):
    """
    Valide le corps de la requête de (dés)activation. BooleanField gère
    correctement aussi bien un JSON natif (true/false) qu'un formulaire
    multipart (chaînes 'true'/'false'/'1'/'0') — contrairement à un simple
    bool(request.data.get(...)), qui interprète à tort la chaîne 'False'
    comme vraie (toute chaîne non vide est truthy en Python).
    """
    actif = serializers.BooleanField(default=False)


class DesactivationCompteAPIView(APIView):
    """
    Base commune : active/désactive le compte Utilisateur derrière un
    profil. Action séparée du PATCH de profil, pour rester explicite et
    auditable plutôt que de mélanger ce changement sensible à une
    modification ordinaire (ex. téléphone).

    Corps attendu : {"actif": true|false}. Absent → désactive par défaut.
    """
    queryset = None
    permission_classes = None

    def post(self, request, pk):
        profil = generics.get_object_or_404(self.queryset, pk=pk)
        serializer = _DesactivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        actif = serializer.validated_data['actif']

        profil.utilisateur.is_active = actif
        profil.utilisateur.save(update_fields=['is_active'])
        return Response(
            {'username': profil.utilisateur.username, 'is_active': actif},
            status=status.HTTP_200_OK,
        )


class AgentDesactivationView(DesactivationCompteAPIView):
    """POST /api/comptes/gestion-utilisateurs/agents/<pk>/desactiver/"""
    queryset = Agent.objects.select_related('utilisateur').all()
    permission_classes = [permissions.IsAuthenticated, PeutModifierModele]


class ClientDesactivationView(DesactivationCompteAPIView):
    """POST /api/comptes/gestion-utilisateurs/clients/<pk>/desactiver/"""
    queryset = Client.objects.select_related('utilisateur').all()
    permission_classes = [permissions.IsAuthenticated, PeutModifierModele]


class AdministrateurDesactivationView(DesactivationCompteAPIView):
    """POST /api/comptes/gestion-utilisateurs/administrateurs/<pk>/desactiver/"""
    queryset = Administrateur.objects.select_related('utilisateur').all()
    permission_classes = [permissions.IsAuthenticated, PeutCreerAdministrateur]