from django.db import migrations, models


class Migration(migrations.Migration):
    """
    RG6 (décision du 18/10/2026) : un client ne peut avoir qu'une réservation non annulée
    par couple (date, créneau). Une réservation annulée libère le créneau.

    Volontairement SANS dépendance vers une migration de comptes : rien ici ne touche à comptes.
    """

    dependencies = [
        ('reservations', '0004_groupe_gerer_abonnements'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.UniqueConstraint(
                condition=models.Q(('statut', 'annulee'), _negated=True),
                fields=('client', 'date_reservation', 'creneau'),
                name='unique_reservation_active_par_client_creneau',
            ),
        ),
    ]