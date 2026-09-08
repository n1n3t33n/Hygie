from django.db import models

from apps.comptes.models import Client


class Frequence(models.TextChoices):
    """
    Fréquence de l'abonnement (07 UML, diagramme de classes v2).
    """
    HEBDOMADAIRE = 'hebdomadaire', 'Hebdomadaire'
    BIMENSUELLE = 'bimensuelle', 'Bimensuelle'
    MENSUELLE = 'mensuelle', 'Mensuelle'


class Abonnement(models.Model):
    """
    Abonnement souscrit par un Client (entité ABONNEMENT du MCD v3).
    Relation SOUSCRIT : Client (1) — Abonnement (0..*) ; chaque abonnement appartient
    à un seul client (cardinalité 1,1 côté Abonnement, corrigée lors de la dérivation
    du MLD — voir 06 MERISE).
    """
    id_abonnement = models.BigAutoField(primary_key=True)
    frequence = models.CharField(max_length=20, choices=Frequence.choices)
    date_debut = models.DateField()
    date_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Null tant que l'abonnement est actif (voir P3, diagramme de séquence).",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='abonnements',
    )

    class Meta:
        db_table = 'abonnement'
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'

    def __str__(self):
        return f"{self.get_frequence_display()} — {self.client}"