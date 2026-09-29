from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.comptes.models.administrateur import Administrateur
from apps.comptes.models.agent import Agent
from apps.comptes.models.client import Client
from apps.comptes.models.utilisateur import Utilisateur
from apps.comptes.models.zone import Zone


class GestionAgentTests(APITestCase):
    """Cas d'utilisation "Gérer les utilisateurs" (07 UML) — CRUD Agent, admin-only."""

    def setUp(self):
        self.url_liste = reverse('comptes:agent-list-create')
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
        reponse = self.client.post(self.url_liste, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        agent = Agent.objects.get(utilisateur__username='agent_test')
        self.assertEqual(agent.utilisateur.get_role(), 'agent')

    def test_refusee_sans_authentification(self):
        reponse = self.client.post(self.url_liste, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_creation_refusee_sans_permission(self):
        utilisateur_lambda = Utilisateur.objects.create_user(
            username='sans_droit', password='MotDePasse#2026Solide'
        )
        self.client.force_authenticate(user=utilisateur_lambda)
        reponse = self.client.post(self.url_liste, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_liste_refusee_sans_permission_view(self):
        utilisateur_lambda = Utilisateur.objects.create_user(
            username='sans_droit_view', password='MotDePasse#2026Solide'
        )
        self.client.force_authenticate(user=utilisateur_lambda)
        reponse = self.client.get(self.url_liste)
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_liste_et_detail_par_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url_liste, self.payload)
        agent = Agent.objects.get(utilisateur__username='agent_test')

        reponse_liste = self.client.get(self.url_liste)
        self.assertEqual(reponse_liste.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reponse_liste.data), 1)

        url_detail = reverse('comptes:agent-detail', kwargs={'pk': agent.pk})
        reponse_detail = self.client.get(url_detail)
        self.assertEqual(reponse_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse_detail.data['telephone'], '+2250700000001')

    def test_modification_telephone_par_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url_liste, self.payload)
        agent = Agent.objects.get(utilisateur__username='agent_test')
        url_detail = reverse('comptes:agent-detail', kwargs={'pk': agent.pk})

        reponse = self.client.patch(url_detail, {'telephone': '+2250700000099'})
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        agent.refresh_from_db()
        self.assertEqual(agent.telephone, '+2250700000099')

    def test_desactivation_et_reactivation_par_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url_liste, self.payload)
        agent = Agent.objects.get(utilisateur__username='agent_test')
        url_desactiver = reverse('comptes:agent-desactiver', kwargs={'pk': agent.pk})

        reponse = self.client.post(url_desactiver, {'actif': False})
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        agent.utilisateur.refresh_from_db()
        self.assertFalse(agent.utilisateur.is_active)

        reponse = self.client.post(url_desactiver, {'actif': True})
        agent.utilisateur.refresh_from_db()
        self.assertTrue(agent.utilisateur.is_active)

    def test_desactivation_refusee_pour_administrateur_limite_sans_capacite(self):
        admin_limite = Utilisateur.objects.create_user(
            username='admin_sans_capacite', password='MotDePasse#2026Solide', is_staff=True,
        )
        Administrateur.objects.create(utilisateur=admin_limite)
        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url_liste, self.payload)
        agent = Agent.objects.get(utilisateur__username='agent_test')
        url_desactiver = reverse('comptes:agent-desactiver', kwargs={'pk': agent.pk})

        self.client.force_authenticate(user=admin_limite)
        reponse = self.client.post(url_desactiver, {'actif': False})
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrateur_avec_groupe_gerer_utilisateurs_peut_desactiver(self):
        groupe = Group.objects.get(name='Administrateur - Gérer les utilisateurs')
        admin_habilite = Utilisateur.objects.create_user(
            username='admin_habilite', password='MotDePasse#2026Solide', is_staff=True,
        )
        admin_habilite.groups.add(groupe)
        Administrateur.objects.create(utilisateur=admin_habilite)

        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url_liste, self.payload)
        agent = Agent.objects.get(utilisateur__username='agent_test')
        url_desactiver = reverse('comptes:agent-desactiver', kwargs={'pk': agent.pk})

        self.client.force_authenticate(user=admin_habilite)
        reponse = self.client.post(url_desactiver, {'actif': False})
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)


class GestionClientTests(APITestCase):
    """CRUD Client côté gestion administrateur (pas de création : auto-inscription uniquement)."""

    def setUp(self):
        self.zone = Zone.objects.create(nom='Cocody', type_zone='quartier_ouvert')
        self.superuser = Utilisateur.objects.create_superuser(
            username='patron', password='MotDePasse#2026Solide'
        )
        utilisateur_client = Utilisateur.objects.create_user(
            username='client_gere', password='MotDePasse#2026Solide',
            first_name='Awa', last_name='Kouassi',
        )
        self.client_obj = Client.objects.create(
            utilisateur=utilisateur_client, telephone='+2250700000002',
            zone=self.zone, point_eau_disponible=True,
        )
        self.url_liste = reverse('comptes:client-list')
        self.url_detail = reverse('comptes:client-detail', kwargs={'pk': self.client_obj.pk})
        self.url_desactiver = reverse('comptes:client-desactiver', kwargs={'pk': self.client_obj.pk})

    def test_liste_et_detail_par_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        reponse = self.client.get(self.url_liste)
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reponse.data), 1)

    def test_desactivation_par_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        reponse = self.client.post(self.url_desactiver, {'actif': False})
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.client_obj.utilisateur.refresh_from_db()
        self.assertFalse(self.client_obj.utilisateur.is_active)

    def test_client_ne_peut_pas_se_desactiver_lui_meme(self):
        self.client.force_authenticate(user=self.client_obj.utilisateur)
        reponse = self.client.post(self.url_desactiver, {'actif': False})
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)


class CreationAdministrateurTests(APITestCase):
    """Capacité "creer_administrateur" — CRUD complet, capacité indivisible."""

    def setUp(self):
        self.url_liste = reverse('comptes:administrateur-list-create')
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
        reponse = self.client.post(self.url_liste, self.payload)
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        administrateur = Administrateur.objects.get(utilisateur__username='admin_partenaire')
        self.assertTrue(administrateur.utilisateur.is_staff)
        self.assertFalse(administrateur.utilisateur.is_superuser)
        self.assertIn(self.groupe, administrateur.utilisateur.groups.all())

    def test_refusee_pour_administrateur_limite_sans_capacite(self):
        admin_limite = Utilisateur.objects.create_user(
            username='admin_limite', password='MotDePasse#2026Solide', is_staff=True,
        )
        Administrateur.objects.create(utilisateur=admin_limite)
        self.client.force_authenticate(user=admin_limite)
        reponse = self.client.post(self.url_liste, {**self.payload, 'username': 'autre_admin'})
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_desactivation_par_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url_liste, self.payload)
        administrateur = Administrateur.objects.get(utilisateur__username='admin_partenaire')
        url_desactiver = reverse('comptes:administrateur-desactiver', kwargs={'pk': administrateur.pk})

        reponse = self.client.post(url_desactiver, {'actif': False})
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        administrateur.utilisateur.refresh_from_db()
        self.assertFalse(administrateur.utilisateur.is_active)