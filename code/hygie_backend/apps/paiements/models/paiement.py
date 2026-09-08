from django.db import models

from apps.reservations.models import Reservation


class ModePaiement(models.TextChoices):
    """
    Moyens de paiement mobile money supportés (RG10).
    """
    WAVE = 'wave', 'Wave'
    ORANGE_MONEY = 'orange_money', 'Orange Money'
    MTN_MONEY = 'mtn_money', 'MTN Money'


class Paiement(models.Model):
    """
    Paiement lié à une Réservation (entité PAIEMENT du MCD v3).
    Relation : Reservation (1) — Paiement (0..*) — acompte + solde possibles
    (07 UML, diagramme de classes v2 : hypothèse de modélisation liée à l'approche
    « dépôt symbolique » validée en Phase 0, à formaliser en RG11 si confirmée à l'usage).

    Intégration mobile money automatisée différée (Wave/Orange Money/MTN Money) :
    en attendant, les paiements sont saisis manuellement depuis le back-office
    (admin ci-dessous) — d'où l'absence volontaire d'un champ statut : un enregistrement
    Paiement signifie un paiement reçu et confirmé.
    """
    id_paiement = models.BigAutoField(primary_key=True)
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.PROTECT,  # historique financier à préserver — à confirmer
        related_name='paiements',
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=ModePaiement.choices)
    date_paiement = models.DateTimeField()

    class Meta:
        db_table = 'paiement'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        return f"Paiement #{self.id_paiement} — {self.montant} FCFA ({self.get_mode_paiement_display()})"