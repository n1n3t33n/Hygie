from django.test import TestCase

from apps.comptes.models.administrateur import Administrateur
from apps.comptes.models.utilisateur import Utilisateur


class BootstrapSuperuserTests(TestCase):
    """Ferme le point ouvert "bootstrap superuser" (createsuperuser)."""

    def test_createsuperuser_cree_automatiquement_le_profil_administrateur(self):
        superuser = Utilisateur.objects.create_superuser(
            username='patron', password='MotDePasse#2026Solide'
        )
        self.assertTrue(Administrateur.objects.filter(utilisateur=superuser).exists())
        self.assertEqual(superuser.get_role(), 'administrateur')

    def test_utilisateur_normal_ne_declenche_pas_le_signal(self):
        utilisateur = Utilisateur.objects.create_user(
            username='client_lambda', password='MotDePasse#2026Solide'
        )
        self.assertFalse(Administrateur.objects.filter(utilisateur=utilisateur).exists())
        self.assertIsNone(utilisateur.get_role())