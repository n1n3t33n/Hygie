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


class MotifAnnulation(models.TextChoices):
    """
    Qui ou quoi a annulé la réservation (renseigné seulement quand le statut est « annulée »).
    Utile pour les remboursements (app paiements) et les statistiques.
    """
    CLIENT = 'client', 'Annulée par le client'
    ADMINISTRATEUR = 'administrateur', 'Annulée par un administrateur'
    EXPIRATION = 'expiration', "Annulée automatiquement (date dépassée sans traitement)"


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
    # Renseigné uniquement pour une réservation annulée ; vide sinon (voir la contrainte).
    motif_annulation = models.CharField(
        max_length=20,
        choices=MotifAnnulation.choices,
        null=True,
        blank=True,
    )
    # CONCERNE : 0,1 côté Réservation (RG5, corrigé lors de la révision v3 du MCD)
    # Décision V2 (validée le 18/10/2026) : PROTECT — un véhicule qui a des réservations
    # ne peut pas être supprimé (SET_NULL détachait silencieusement l'historique).
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.PROTECT,
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
        constraints = [
            # RG6 (décision du 18/10/2026) : un client n'a qu'une réservation NON ANNULÉE par
            # couple (date, créneau). Garde-fou en base ; le contrôle avec message clair est
            # fait en amont par services/reservations.py.
            models.UniqueConstraint(
                fields=['client', 'date_reservation', 'creneau'],
                condition=~models.Q(statut='annulee'),
                name='unique_reservation_active_par_client_creneau',
            ),
            # Un motif d'annulation n'a de sens que pour une réservation annulée.
            models.CheckConstraint(
                condition=models.Q(statut='annulee') | models.Q(motif_annulation__isnull=True),
                name='motif_annulation_seulement_si_annulee',
            ),
        ]

    def __str__(self):
        return f"Réservation #{self.id_reservation} — {self.client} ({self.get_statut_display()})"