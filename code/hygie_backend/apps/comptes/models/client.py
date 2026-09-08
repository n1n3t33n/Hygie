from django.conf import settings
from django.db import models

from .zone import Zone


class Client(models.Model):
    """
    Profil métier Client (entité CLIENT du MCD v3), lié 1-1 à un Utilisateur (authentification).

    Écart volontaire par rapport au MPD d'origine : celui-ci prévoyait id_client comme clé
    autonome (BigAutoField indépendant). Ici, la clé primaire de Client EST la clé étrangère
    vers Utilisateur (OneToOneField en primary_key=True) : un Client ne peut pas exister sans
    Utilisateur associé. Cohérent avec la décision "profils Client/Agent liés en 1-1" prise
    pour l'architecture Django — fonctionnellement équivalent à l'origine (identifiant unique
    BigInt), juste porté par la relation plutôt que par une colonne séparée.

    nom/prénom : portés par Utilisateur.last_name / Utilisateur.first_name (hérités
    d'AbstractUser), volontairement pas dupliqués ici.
    """
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='client',
    )
    telephone = models.CharField(max_length=20)
    # Cardinalité MCD : 1 Zone -- 0..* Client => chaque Client a exactement 1 Zone (FK obligatoire).
    zone = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,  # empêche de supprimer une Zone qui a encore des Clients
        related_name='clients',
    )
    point_eau_disponible = models.BooleanField(
        default=False,
        help_text="RG1 : un point d'eau accessible est requis pour pouvoir réserver.",
    )

    class Meta:
        db_table = 'client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.utilisateur.get_full_name() or self.utilisateur.username