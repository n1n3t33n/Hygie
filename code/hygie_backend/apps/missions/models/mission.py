from django.db import models

from apps.comptes.models import Agent
from apps.reservations.models import Reservation

from .tournee import Tournee


class Mission(models.Model):
    """
    Mission d'exécution d'un lavage (entité MISSION du MCD v3).

    États dérivés, pas d'attribut statut littéral (07 UML, diagramme d'états-transitions) :
    planifiee (demarree_le=null), en_cours (demarree_le≠null, terminee_le=null),
    terminee (demarree_le≠null, terminee_le≠null).

    Contraintes CHECK ci-dessous : réplication exacte des règles RG2/RG7 déjà testées
    dans le script DDL MPD (06 MERISE) — rien de nouveau inventé ici, à revérifier une
    fois les migrations lancées (comportement CheckConstraint sur champs fichier à tester).
    """
    id_mission = models.BigAutoField(primary_key=True)
    # OneToOne : Reservation (1) — Mission (0..1) — chaque réservation a au plus 1 mission.
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.PROTECT,  # historique opérationnel à préserver — à confirmer
        related_name='mission',
    )
    tournee = models.ForeignKey(
        Tournee,
        on_delete=models.PROTECT,
        related_name='missions',
    )
    # REALISE : Agent (1..*) — Mission (0..*), many-to-many sans colonne propre.
    agents = models.ManyToManyField(
        Agent,
        through='Realise',
        related_name='missions',
    )
    demarree_le = models.DateTimeField(null=True, blank=True)
    terminee_le = models.DateTimeField(null=True, blank=True)
    # RG2 : obligatoires respectivement au démarrage et à la fin, pas à la création.
    photo_avant = models.ImageField(upload_to='missions/photos/%Y/%m/', blank=True)
    photo_apres = models.ImageField(upload_to='missions/photos/%Y/%m/', blank=True)

    class Meta:
        db_table = 'mission'
        verbose_name = 'Mission'
        verbose_name_plural = 'Missions'
        constraints = [
            models.CheckConstraint(
                # RG7 : terminée seulement si démarrée au préalable
                check=models.Q(terminee_le__isnull=True) | models.Q(demarree_le__isnull=False),
                name='mission_terminee_apres_demarree',
            ),
            models.CheckConstraint(
                # RG2 : photo avant obligatoire dès que démarrée
                check=models.Q(demarree_le__isnull=True) | ~models.Q(photo_avant=''),
                name='mission_photo_avant_si_demarree',
            ),
            models.CheckConstraint(
                # RG2 : photo après obligatoire dès que terminée
                check=models.Q(terminee_le__isnull=True) | ~models.Q(photo_apres=''),
                name='mission_photo_apres_si_terminee',
            ),
        ]

    def __str__(self):
        return f"Mission #{self.id_mission} — {self.reservation}"