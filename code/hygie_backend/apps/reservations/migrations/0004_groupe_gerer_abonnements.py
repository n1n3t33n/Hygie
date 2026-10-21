from django.apps import apps as apps_reels
from django.contrib.auth.management import create_permissions
from django.db import migrations

NOM_GROUPE = 'Administrateur - Gérer les abonnements'
CODENAMES = ['view_abonnement', 'add_abonnement', 'change_abonnement']


def creer_groupe_gerer_abonnements(apps, schema_editor):
    """
    Capacité « gérer les abonnements » (décision du 19/10/2026) : consulter, créer pour un
    client et modifier la date de fin. Aucune permission de suppression : un abonnement ne
    s'efface pas, on y met fin. Le groupe est créé ici, dans l'app qui possède le modèle
    Abonnement, pour respecter le sens des dépendances (reservations -> comptes).

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


def supprimer_groupe_gerer_abonnements(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=NOM_GROUPE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_groupe_consulter_vehicules'),
    ]

    operations = [
        migrations.RunPython(creer_groupe_gerer_abonnements, supprimer_groupe_gerer_abonnements),
    ]