from django.db import models

from apps.missions.models import Mission


class TypeSignalement(models.TextChoices):
    """
    Origine du signalement (unification client/agent — 07 UML, diagramme de classes v2).
    """
    CLIENT = 'client', 'Client'
    AGENT = 'agent', 'Agent'


class Signalement(models.Model):
    """
    Signalement d'une anomalie liée à une Mission (entité SIGNALEMENT du MCD v3).
    Relation : Mission (1) — Signalement (0..*), FK standard.
    typeSignalement unifie les signalements client et agent (déjà justifié en MERISE).
    """
    id_signalement = models.BigAutoField(primary_key=True)
    mission = models.ForeignKey(
        Mission,
        on_delete=models.PROTECT,  # historique d'incidents à préserver — à confirmer
        related_name='signalements',
    )
    type_signalement = models.CharField(max_length=10, choices=TypeSignalement.choices)
    description = models.TextField()

    class Meta:
        db_table = 'signalement'
        verbose_name = 'Signalement'
        verbose_name_plural = 'Signalements'

    def __str__(self):
        return f"Signalement #{self.id_signalement} — {self.get_type_signalement_display()} ({self.mission})"