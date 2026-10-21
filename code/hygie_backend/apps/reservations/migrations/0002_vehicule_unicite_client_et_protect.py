import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Sous-étape Vehicule (décisions V1 et V2 du 18/10/2026).

    Volontairement SANS dépendance vers une migration de comptes : rien ici ne touche à
    comptes (le lien Client existe depuis 0001, qui dépend déjà de comptes/0002).
    """

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        # V2 : un véhicule référencé par des réservations ne peut plus être supprimé
        # (SET_NULL détachait silencieusement l'historique). Changement purement applicatif.
        migrations.AlterField(
            model_name='reservation',
            name='vehicule',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reservations',
                to='reservations.vehicule',
            ),
        ),
        # V1 : une même immatriculation n'est enregistrable qu'une fois par client.
        migrations.AddConstraint(
            model_name='vehicule',
            constraint=models.UniqueConstraint(
                fields=('client', 'immatriculation'),
                name='unique_immatriculation_par_client',
            ),
        ),
    ]