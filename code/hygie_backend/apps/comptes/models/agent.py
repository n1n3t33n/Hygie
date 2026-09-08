from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    """
    Rôle de l'Agent (entité AGENT du MCD v3, attribut role).
    Traduction fidèle de la généralisation UML "Chef d'équipe hérite d'Agent laveur" :
    une seule classe Agent, différenciée par ce champ plutôt que par des sous-classes Django.
    """
    AGENT_LAVEUR = 'agent_laveur', 'Agent laveur'
    CHEF_EQUIPE = 'chef_equipe', "Chef d'équipe"


class Agent(models.Model):
    """
    Profil métier Agent (entité AGENT du MCD v3), lié 1-1 à un Utilisateur.
    Même écart volontaire que Client : la PK est la FK vers Utilisateur.

    nom : porté par Utilisateur.last_name / Utilisateur.first_name (hérités d'AbstractUser).
    """
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='agent',
    )
    telephone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AGENT_LAVEUR)

    class Meta:
        db_table = 'agent'
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return f"{self.utilisateur.get_full_name() or self.utilisateur.username} ({self.get_role_display()})"