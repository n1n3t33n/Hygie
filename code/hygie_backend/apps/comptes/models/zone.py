from django.db import models


class TypeZone(models.TextChoices):
    """
    Types de zones desservies (07 UML, diagramme de classes v2).
    compound_ferme : lotissement fermé/gardienné.
    quartier_ouvert : quartier résidentiel classique, accès libre.
    Distinction pertinente pour la sécurité des agents en horaire de nuit (RG3 : créneaux 20h-00h).
    """
    COMPOUND_FERME = 'compound_ferme', 'Compound fermé'
    QUARTIER_OUVERT = 'quartier_ouvert', 'Quartier ouvert'


class Zone(models.Model):
    """
    Zone desservie par Hygie Sanitaire (entité ZONE du MCD v3).
    Gérée par l'Administrateur (cas d'utilisation "Gérer les zones desservies", 07 UML).
    """
    id_zone = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    type_zone = models.CharField(max_length=20, choices=TypeZone.choices)

    class Meta:
        db_table = 'zone'
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'

    def __str__(self):
        return self.nom