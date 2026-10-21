from django.apps import apps as apps_reels
from django.contrib.auth.management import create_permissions
from django.db import migrations

NOM_GROUPE = 'Administrateur - Gérer les réservations'
CODENAMES = ['view_reservation', 'change_reservation']


def creer_groupe_gerer_reservations(apps, schema_editor):
    """
    Capacité « gérer les réservations » (décision R2, validée le 18/10/2026) : voir toutes les
    réservations, les confirmer, les terminer et les annuler. Aucune permission d'ajout ni de
    suppression : seul un Client crée ses réservations, et une réservation ne s'efface pas
    (on l'annule). Le groupe est créé ici, dans l'app qui possède le modèle Reservation, pour
    respecter le sens des dépendances (reservations -> comptes).

    Les permissions standards ne sont normalement créées qu'APRÈS toutes les migrations
    (signal post_migrate) ; on force leur création pour pouvoir les référencer ici
    (même contournement que comptes/0006 et reservations/0003).
    """
    create_permissions(apps_reels.get_app_config('reservations'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    permissions = Permission.objects.filter(
        content_type__app_label='reservations', codename__in=CODENAMES,
    )
    groupe, _ = Group.objects.get_or_create(name=NOM_GROUPE)
    groupe.permissions.set(permissions)


def supprimer_groupe_gerer_reservations(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=NOM_GROUPE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_reservation_unicite_creneau'),
    ]

    operations = [
        migrations.RunPython(creer_groupe_gerer_reservations, supprimer_groupe_gerer_reservations),
    ]