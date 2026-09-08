from django.db import models

from apps.comptes.models import Agent


class Tournee(models.Model):
    """
    Tournée créée par un Chef d'équipe pour regrouper plusieurs missions
    (entité TOURNEE du MCD v3).

    Le regroupement de réservations avant création d'une tournée est mentionné dans le
    MCT mais sans règle de gestion numérotée (07 UML, diagramme d'activité — noté sans
    être inventé).
    """
    id_tournee = models.BigAutoField(primary_key=True)
    date_tournee = models.DateField()
    # Association "(créateur)" du diagramme de classes v2 : Agent (1) — Tournee (0..*).
    # Restriction métier {role=chef_equipe} (creerTournee(), diagramme de classes v2) —
    # à valider côté service applicatif (09 Backend Django), pas ici au niveau du modèle.
    createur = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,  # traçabilité — à confirmer
        related_name='tournees_creees',
    )

    class Meta:
        db_table = 'tournee'
        verbose_name = 'Tournée'
        verbose_name_plural = 'Tournées'

    def __str__(self):
        return f"Tournée #{self.id_tournee} — {self.date_tournee}"