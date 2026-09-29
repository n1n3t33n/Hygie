from django.apps import apps as apps_reels
from django.contrib.auth.management import create_permissions
from django.db import migrations


def creer_groupes_capacites(apps, schema_editor):
    """
    Les permissions standards (add_*, change_*, etc.) et personnalisées
    (creer_administrateur, voir_statistiques) ne sont normalement créées
    qu'APRÈS toutes les migrations, via le signal post_migrate. On force
    leur création ici pour pouvoir les référencer dans cette même migration
    (contournement documenté officiellement par Django pour ce cas précis).
    """
    create_permissions(apps_reels.get_app_config('comptes'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    def perm(codename):
        return Permission.objects.get(content_type__app_label='comptes', codename=codename)

    zones, _ = Group.objects.get_or_create(name='Administrateur - Gérer les zones')
    zones.permissions.set([perm('add_zone'), perm('change_zone'), perm('delete_zone'), perm('view_zone')])

    utilisateurs, _ = Group.objects.get_or_create(name='Administrateur - Gérer les utilisateurs')
    utilisateurs.permissions.set([
        perm('add_agent'), perm('change_agent'), perm('delete_agent'), perm('view_agent'),
        perm('view_client'), perm('change_client'),
    ])

    statistiques, _ = Group.objects.get_or_create(name='Administrateur - Consulter les statistiques')
    statistiques.permissions.set([perm('voir_statistiques')])

    # "Administrateur - Gérer les tarifs" volontairement absent : le modèle
    # Tarif n'est pas encore rattaché à une app dans les diagrammes UML.


def supprimer_groupes_capacites(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=[
        'Administrateur - Gérer les zones',
        'Administrateur - Gérer les utilisateurs',
        'Administrateur - Consulter les statistiques',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0005_alter_administrateur_options'),
    ]

    operations = [
        migrations.RunPython(creer_groupes_capacites, supprimer_groupes_capacites),
    ]