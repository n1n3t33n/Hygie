from django.contrib.auth.models import Group
from django.db import transaction

from rest_framework import serializers

from apps.comptes.models.administrateur import Administrateur
from apps.comptes.models.agent import Agent
from apps.comptes.models.client import Client
from apps.comptes.serializers.base import CompteMixin, ProfilDetailMixin


class AgentCreationSerializer(CompteMixin, serializers.ModelSerializer):
    """Création d'un compte Agent — pas d'auto-inscription (07 UML)."""

    class Meta:
        model = Agent
        fields = ['username', 'password', 'email', 'nom', 'prenom', 'telephone', 'role']

    @transaction.atomic
    def create(self, validated_data):
        utilisateur = self._creer_utilisateur(validated_data)
        return Agent.objects.create(utilisateur=utilisateur, **validated_data)


class AgentDetailSerializer(ProfilDetailMixin, serializers.ModelSerializer):
    """Liste, consultation et modification d'un Agent existant."""

    class Meta:
        model = Agent
        fields = ['username', 'email', 'nom', 'prenom', 'is_active', 'telephone', 'role']
        read_only_fields = ['username', 'email', 'nom', 'prenom', 'is_active']


class ClientDetailSerializer(ProfilDetailMixin, serializers.ModelSerializer):
    """
    Liste, consultation et modification d'un Client existant. Pas de
    serializer de création côté gestion : le Client s'inscrit lui-même
    (voir serializers/inscription.py).
    """

    class Meta:
        model = Client
        fields = ['username', 'email', 'nom', 'prenom', 'is_active', 'telephone', 'zone', 'point_eau_disponible']
        read_only_fields = ['username', 'email', 'nom', 'prenom', 'is_active']


class AdministrateurCreationSerializer(CompteMixin, serializers.ModelSerializer):
    """
    Création d'un compte Administrateur par un Administrateur déjà habilité
    (permission "comptes.creer_administrateur").

    groupes : noms de Group Django à assigner (capacités). Optionnel — un
    Administrateur créé sans groupe n'a AUCUNE capacité par défaut au-delà
    de l'authentification (is_staff=True).
    """
    groupes = serializers.ListField(
        child=serializers.CharField(), required=False, default=list, write_only=True,
    )

    class Meta:
        model = Administrateur
        fields = ['username', 'password', 'email', 'nom', 'prenom', 'groupes']

    @transaction.atomic
    def create(self, validated_data):
        noms_groupes = validated_data.pop('groupes', [])
        utilisateur = self._creer_utilisateur(validated_data)
        utilisateur.is_staff = True
        utilisateur.save(update_fields=['is_staff'])
        if noms_groupes:
            utilisateur.groups.set(Group.objects.filter(name__in=noms_groupes))
        return Administrateur.objects.create(utilisateur=utilisateur)


class AdministrateurDetailSerializer(ProfilDetailMixin, serializers.ModelSerializer):
    """
    Liste et consultation d'un Administrateur existant. Lecture seule :
    Administrateur ne porte aucun champ métier propre (voir le modèle) —
    rien à modifier ici. La réaffectation de groupes reste une action
    future séparée, hors périmètre de cette étape.
    """

    class Meta:
        model = Administrateur
        fields = ['username', 'email', 'nom', 'prenom', 'is_active']