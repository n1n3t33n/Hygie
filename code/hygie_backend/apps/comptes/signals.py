from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.comptes.models.administrateur import Administrateur


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_profil_administrateur_superuser(sender, instance, created, **kwargs):
    """
    Bootstrap : `createsuperuser` (ou toute création directe d'un Utilisateur
    avec is_superuser=True) ne crée pas de profil Administrateur — or les
    permissions basées sur get_role() (IsAdministrateur) exigent ce profil.
    Ce signal comble l'écart automatiquement, uniquement à la création, et
    uniquement si aucun profil n'existe déjà — garde l'exclusivité intacte :
    ne s'applique jamais si l'Utilisateur porte déjà Client ou Agent (cas
    normalement impossible pour un superuser créé via createsuperuser, mais
    la garde reste utile en défense).
    """
    if not created or not instance.is_superuser:
        return
    if hasattr(instance, 'administrateur') or hasattr(instance, 'client') or hasattr(instance, 'agent'):
        return
    Administrateur.objects.create(utilisateur=instance)