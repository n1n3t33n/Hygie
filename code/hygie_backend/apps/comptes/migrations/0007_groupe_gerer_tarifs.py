from django.apps import apps as apps_reels
from django.contrib.auth.management import create_permissions
from django.db import migrations


def creer_groupe_tarifs(apps, schema_editor):
    """
    Complète les groupes de capacités administrateur avec "Gérer les tarifs"
    (07 UML). Le modèle Tarif vit dans l'app paiements (confirmé par
    dix-neuf) — jusqu'ici non déterminable (écart UML documenté).
    """
    create_permissions(apps_reels.get_app_config('paiements'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    def perm(codename):
        return Permission.objects.get(content_type__app_label='paiements', codename=codename)

    tarifs, _ = Group.objects.get_or_create(name='Administrateur - Gérer les tarifs')
    tarifs.permissions.set([
        perm('add_tarif'), perm('change_tarif'), perm('delete_tarif'), perm('view_tarif'),
    ])


def supprimer_groupe_tarifs(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Administrateur - Gérer les tarifs').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0006_creer_groupes_capacites_administrateur'),
        ('paiements', '0001_initial'),  # ⚠️ remplace par le vrai nom de la migration qui crée Tarif
    ]

    operations = [
        migrations.RunPython(creer_groupe_tarifs, supprimer_groupe_tarifs),
    ]