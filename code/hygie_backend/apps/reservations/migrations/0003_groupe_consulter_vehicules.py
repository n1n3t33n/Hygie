from django.apps import apps as apps_reels
from django.contrib.auth.management import create_permissions
from django.db import migrations

NOM_GROUPE = 'Administrateur - Consulter les véhicules'


def creer_groupe_consulter_vehicules(apps, schema_editor):
    """
    Capacité « consulter les véhicules » (décision V3, validée le 18/10/2026) : lecture seule,
    via la permission Django native view_vehicule. Le groupe est créé ici, dans l'app qui
    possède le modèle Vehicule, et non dans comptes : comptes ne doit pas dépendre de
    reservations (sens des dépendances du diagramme de packages).

    Les permissions standards ne sont normalement créées qu'APRÈS toutes les migrations
    (signal post_migrate) ; on force leur création pour pouvoir les référencer ici
    (même contournement que comptes/0006).
    """
    create_permissions(apps_reels.get_app_config('reservations'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    permission = Permission.objects.get(
        content_type__app_label='reservations', codename='view_vehicule',
    )
    groupe, _ = Group.objects.get_or_create(name=NOM_GROUPE)
    groupe.permissions.set([permission])


def supprimer_groupe_consulter_vehicules(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=NOM_GROUPE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_vehicule_unicite_client_et_protect'),
    ]

    operations = [
        migrations.RunPython(creer_groupe_consulter_vehicules, supprimer_groupe_consulter_vehicules),
    ]