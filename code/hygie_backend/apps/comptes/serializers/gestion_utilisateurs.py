from django.contrib.auth.models import Group
from django.db import transaction

from rest_framework import serializers

from apps.comptes.models.administrateur import Administrateur
from apps.comptes.models.agent import Agent
from apps.comptes.serializers.base import CompteMixin


class AgentCreationSerializer(CompteMixin, serializers.ModelSerializer):
    """
    Création d'un compte Agent (agent_laveur ou chef_equipe) par un
    Administrateur — pas d'auto-inscription pour ce rôle : absent des cas
    d'utilisation Agent laveur / Chef d'équipe (07 UML).
    """

    class Meta:
        model = Agent
        fields = ['username', 'password', 'email', 'nom', 'prenom', 'telephone', 'role']

    @transaction.atomic
    def create(self, validated_data):
        utilisateur = self._creer_utilisateur(validated_data)
        return Agent.objects.create(utilisateur=utilisateur, **validated_data)


class AdministrateurCreationSerializer(CompteMixin, serializers.ModelSerializer):
    """
    Création d'un compte Administrateur par un Administrateur déjà habilité
    (permission "comptes.creer_administrateur"). Écart par rapport au 07 UML,
    qui ne documente qu'un acteur Administrateur unique — à consigner dans
    Notion avec l'écart déjà loggé sur l'existence même du profil.

    groupes : noms de Group Django à assigner (capacités), ex.
    ["Administrateur Lavage Partenaire"]. Optionnel — un Administrateur créé
    sans groupe n'a AUCUNE capacité par défaut au-delà de l'authentification
    (is_staff=True) : les capacités s'accordent toujours explicitement.
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