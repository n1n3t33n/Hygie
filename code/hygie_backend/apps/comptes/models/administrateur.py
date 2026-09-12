from django.conf import settings
from django.db import models


class Administrateur(models.Model):
    """
    Profil métier Administrateur (rattaché 1-1 à un Utilisateur, authentification).

    Écart volontaire par rapport au MCD v3 validé : cette entité n'existe pas dans
    le modèle conceptuel documenté (12 entités). Elle est ajoutée au niveau Django
    pour suivre le même patron que Client et Agent (profil applicatif OneToOne) et
    distinguer explicitement le rôle Administrateur des rôles Client et Agent/Chef
    d'équipe. Écart à consigner dans Notion (06 MERISE) une fois le quota de blocs
    débloqué.

    Profil volontairement minimal : aucun attribut métier propre pour l'instant.
    """
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='administrateur',
    )

    class Meta:
        db_table = 'administrateur'
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'

    def __str__(self):
        return self.utilisateur.get_full_name() or self.utilisateur.username