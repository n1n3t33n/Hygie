from django.db import models

from apps.comptes.models import Agent

from .mission import Mission


class Realise(models.Model):
    """
    Table de jonction REALISE (Agent ↔ Mission), sans colonne propre — traduction directe
    de l'association many-to-many du diagramme de classes v2 (Agent 1..* — 0..* Mission),
    pas une classe-association (décision déjà actée en 07 UML).
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'realise'
        unique_together = ('agent', 'mission')
        verbose_name = 'Réalisation (Agent × Mission)'
        verbose_name_plural = 'Réalisations (Agent × Mission)'

    def __str__(self):
        return f"{self.agent} — {self.mission}"