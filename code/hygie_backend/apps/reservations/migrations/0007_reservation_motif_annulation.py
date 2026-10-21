from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Motif d'annulation d'une réservation (décision du 21/10/2026) : client, administrateur ou
    expiration automatique. Vide pour une réservation non annulée ; les éventuelles
    réservations déjà annulées avant cette migration gardent un motif vide.

    Volontairement SANS dépendance vers une migration de comptes : rien ici ne touche à comptes.
    """

    dependencies = [
        ('reservations', '0006_groupe_gerer_reservations'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='motif_annulation',
            field=models.CharField(
                blank=True,
                choices=[
                    ('client', 'Annulée par le client'),
                    ('administrateur', 'Annulée par un administrateur'),
                    ('expiration', 'Annulée automatiquement (date dépassée sans traitement)'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ('statut', 'annulee'),
                    ('motif_annulation__isnull', True),
                    _connector='OR',
                ),
                name='motif_annulation_seulement_si_annulee',
            ),
        ),
    ]