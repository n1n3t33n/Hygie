from django.db import models

from apps.comptes.models import Client

from .abonnement import Abonnement
from .vehicule import Vehicule


class Creneau(models.TextChoices):
    """
    Créneaux horaires proposés (RG3 : sécurité des agents en horaire de nuit).
    """
    MATIN = 'matin', 'Matin (4h–6h30)'
    SOIR = 'soir', 'Soir (20h–00h)'


class StatutReservation(models.TextChoices):
    """
    Statut de la réservation (07 UML, diagramme de classes v2 ; diagramme d'états-transitions).
    """
    EN_ATTENTE = 'en_attente', 'En attente'
    CONFIRMEE = 'confirmee', 'Confirmée'
    ANNULEE = 'annulee', 'Annulée'
    TERMINEE = 'terminee', 'Terminée'


class Reservation(models.Model):
    """
    Réservation d'un lavage (entité RESERVATION du MCD v3).

    Écart volontaire par rapport au MCD v3 validé (décidé le 8 septembre 2026, en session
    de développement) : ajout d'un FK obligatoire vers Client. Le MCD d'origine ne relie
    Reservation à Client qu'indirectement, via Vehicule (0..1) ou Abonnement (0..1) — tous
    deux optionnels, ce qui laissait certaines réservations sans propriétaire traçable.
    À reporter dans 06 MERISE lors d'une prochaine validation Notion si tu le souhaites.
    """
    id_reservation = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,  # historique transactionnel à préserver — à confirmer
        related_name='reservations',
    )
    date_reservation = models.DateField()
    creneau = models.CharField(max_length=10, choices=Creneau.choices)
    statut = models.CharField(
        max_length=20,
        choices=StatutReservation.choices,
        default=StatutReservation.EN_ATTENTE,
    )
    # CONCERNE : 0,1 côté Réservation (RG5, corrigé lors de la révision v3 du MCD)
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
    )
    # Lien optionnel Abonnement↔Réservation (07 UML, diagramme de classes v2)
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
    )

    class Meta:
        db_table = 'reservation'
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'

    def __str__(self):
        return f"Réservation #{self.id_reservation} — {self.client} ({self.get_statut_display()})"