from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.comptes.models.administrateur import Administrateur
from apps.comptes.models.agent import Agent
from apps.comptes.models.utilisateur import Utilisateur


class CreationAgentTests(APITestCase):
    """Cas d'utilisation "Gérer les utilisateurs" (07 UML) — création Agent, admin-only."""

    def setUp(self):
        self.url = reverse('comptes:agent-creation')
        self.superuser = Utilisateur.objects.create_superuser(
            username='patron', password='MotDePasse#2026Solide'
        )
        self.payload = {
            'username': 'agent_test', 'password': 'MotDePasse#2026Solide',
            'nom': 'Yao', 'prenom': 'Kofi', 'telephone': '+2250700000001',
            'role': 'agent_laveur',
        }

    def test_creation_par_superuser_reussie(self):
        self.client.force_authenticate(user=self.superuser)
        reponse = self.client.post(self.url, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        agent = Agent.objects.get(utilisateur__username='agent_test')
        self.assertEqual(agent.utilisateur.get_role(), 'agent')

    def test_refusee_sans_authentification(self):
        reponse = self.client.post(self.url, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refusee_sans_permission(self):
        utilisateur_lambda = Utilisateur.objects.create_user(
            username='sans_droit', password='MotDePasse#2026Solide'
        )
        self.client.force_authenticate(user=utilisateur_lambda)
        reponse = self.client.post(self.url, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)


class CreationAdministrateurTests(APITestCase):
    """Capacité "creer_administrateur" — distincte du simple rôle Administrateur."""

    def setUp(self):
        self.url = reverse('comptes:administrateur-creation')
        self.superuser = Utilisateur.objects.create_superuser(
            username='patron', password='MotDePasse#2026Solide'
        )
        self.groupe = Group.objects.create(name='Administrateur Lavage Partenaire')
        self.payload = {
            'username': 'admin_partenaire', 'password': 'MotDePasse#2026Solide',
            'nom': 'Diallo', 'prenom': 'Fatou', 'groupes': ['Administrateur Lavage Partenaire'],
        }

    def test_creation_par_superuser_avec_groupes(self):
        self.client.force_authenticate(user=self.superuser)
        reponse = self.client.post(self.url, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        administrateur = Administrateur.objects.get(utilisateur__username='admin_partenaire')
        self.assertTrue(administrateur.utilisateur.is_staff)
        self.assertFalse(administrateur.utilisateur.is_superuser)
        self.assertIn(self.groupe, administrateur.utilisateur.groups.all())

    def test_refusee_pour_administrateur_limite_sans_capacite(self):
        # Un Administrateur limité, même authentifié, n'a pas creer_administrateur par défaut.
        admin_limite = Utilisateur.objects.create_user(
            username='admin_limite', password='MotDePasse#2026Solide', is_staff=True,
        )
        Administrateur.objects.create(utilisateur=admin_limite)
        self.client.force_authenticate(user=admin_limite)
        reponse = self.client.post(self.url, {**self.payload, 'username': 'autre_admin'})
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)