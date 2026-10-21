from django.db import models

from apps.comptes.models import Client


class TypeVehicule(models.TextChoices):
    """
    Types de véhicules pris en charge (07 UML, diagramme de classes v2).
    """
    CITADINE = 'citadine', 'Citadine'
    BERLINE = 'berline', 'Berline'
    SUV_4X4 = 'suv_4x4', 'SUV / 4x4'
    UTILITAIRE = 'utilitaire', 'Utilitaire'


class Vehicule(models.Model):
    """
    Véhicule appartenant à un Client (entité VEHICULE du MCD v3).
    Relation POSSEDE : Client (1) — Vehicule (0..*).
    """
    id_vehicule = models.BigAutoField(primary_key=True)
    immatriculation = models.CharField(max_length=20)
    type_vehicule = models.CharField(max_length=20, choices=TypeVehicule.choices)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,  # un véhicule n'a pas de sens sans son propriétaire — à confirmer
        related_name='vehicules',
    )

    class Meta:
        db_table = 'vehicule'
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        constraints = [
            # Décision V1 (validée le 18/10/2026) : une même plaque ne peut être enregistrée
            # qu'une fois PAR CLIENT. Garde-fou en base ; la normalisation (espaces, majuscules)
            # est faite en amont par services/vehicules.py.
            models.UniqueConstraint(
                fields=['client', 'immatriculation'],
                name='unique_immatriculation_par_client',
            ),
        ]

    def __str__(self):
        return f"{self.immatriculation} ({self.get_type_vehicule_display()})"