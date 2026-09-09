from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.missions.models import Mission


class Avis(models.Model):
    """
    Avis déposé par le Client sur une Mission terminée (entité AVIS du MCD v3).
    Relation : Mission (1) — Avis (0..1), OneToOneField (07 UML, diagramme de classes v2).

    RG9 : une notation ne peut être déposée qu'après que la mission soit "terminée"
    (mission.terminee_le ≠ null). Non contraignable en CHECK SQL classique (référence un
    champ d'une autre table) — à faire respecter côté service applicatif (09 Backend
    Django : "aucune logique métier dans les views"), pas ici au niveau du modèle.
    """
    id_avis = models.BigAutoField(primary_key=True)
    mission = models.OneToOneField(
        Mission,
        on_delete=models.PROTECT,  # historique de satisfaction à préserver — à confirmer
        related_name='avis',
    )
    note = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    # Non marqué optionnel en UML, mais assomption : un client peut noter sans commenter.
    commentaire = models.TextField(blank=True)

    class Meta:
        db_table = 'avis'
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'

    def __str__(self):
        return f"Avis #{self.id_avis} — {self.note}/5 ({self.mission})"