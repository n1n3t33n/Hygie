from rest_framework import generics, permissions

from apps.comptes.serializers.inscription import ClientInscriptionSerializer


class ClientInscriptionView(generics.CreateAPIView):
    """POST /api/comptes/inscription/ — public, seul le Client s'auto-inscrit."""
    serializer_class = ClientInscriptionSerializer
    permission_classes = [permissions.AllowAny]