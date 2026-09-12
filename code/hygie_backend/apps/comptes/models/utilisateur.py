from django.contrib.auth.models import AbstractUser
from django.db import models

from .agent import Role as AgentRole


class Utilisateur(AbstractUser):
    """
    Modèle d'authentification unique (AUTH_USER_MODEL).
    Porte uniquement la connexion et les permissions Django (is_staff, is_superuser).

    Rôle métier déterminé par le profil OneToOne rattaché :
      - Client         -> utilisateur.client
      - Agent          -> utilisateur.agent (voir Agent.role : agent_laveur / chef_equipe)
      - Administrateur -> utilisateur.administrateur

    Un Utilisateur ne doit porter qu'un seul de ces trois profils à la fois.
    Cette exclusivité n'est pas garantie au niveau base de données (OneToOne inversé
    ne le permet pas nativement) — à appliquer au niveau des serializers de
    création de compte (étape à venir, par app).

    Le rôle métier ("client" / "agent" / "chef_equipe" / "administrateur") est
    calculé dynamiquement via get_role() et exposé comme claim JWT "role"
    (voir UtilisateurTokenObtainPairSerializer).
    """
    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def get_role(self):
        """
        Calcule le rôle métier à partir du profil rattaché.
        Retourne 'administrateur', 'chef_equipe', 'agent', 'client',
        ou None si aucun profil n'est encore rattaché (cas transitoire : compte
        superutilisateur créé via createsuperuser, avant création manuelle
        du profil Administrateur correspondant — voir remarque plus bas).
        Ordre de priorité (administrateur > agent > client) : garde-fou en cas
        de données incohérentes, ne remplace pas la validation à l'inscription.
        """
        if hasattr(self, 'administrateur'):
            return 'administrateur'
        if hasattr(self, 'agent'):
            return 'chef_equipe' if self.agent.role == AgentRole.CHEF_EQUIPE else 'agent'
        if hasattr(self, 'client'):
            return 'client'
        return None

    def __str__(self):
        return self.get_full_name() or self.username