from django.db import models


class Tarif(models.Model):
    """
    Catalogue des tarifs pratiqués — 12e entité, ajoutée rétroactivement au MCD v3
    (absente du MCD/diagramme de classes v2 d'origine ; comble l'écart explicitement
    noté dans 07 UML, diagramme de séquence P7).

    Consultable par l'Administrateur (cas d'utilisation "Gérer les tarifs", 07 UML).
    Volontairement SANS lien en base avec Reservation/Abonnement/Paiement pour l'instant
    (décision prise le 07/09/2026) : le montant réellement facturé reste saisi librement
    sur Paiement.
    """
    id_tarif = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'tarif'
        verbose_name = 'Tarif'
        verbose_name_plural = 'Tarifs'

    def __str__(self):
        return f"{self.nom} — {self.prix} FCFA"