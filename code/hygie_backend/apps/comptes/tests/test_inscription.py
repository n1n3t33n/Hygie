from django.contrib.auth.password_validation import password_validators_help_texts  # noqa: F401 (référence, non utilisé directement)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.comptes.models.client import Client
from apps.comptes.models.utilisateur import Utilisateur
from apps.comptes.models.zone import Zone


class InscriptionClientTests(APITestCase):
    """Cas d'utilisation "S'inscrire" (07 UML) — flux public P1."""

    def setUp(self):
        self.zone = Zone.objects.create(nom='Cocody', type_zone='quartier_ouvert')
        self.url = reverse('comptes:client-inscription')
        self.payload_valide = {
            'username': 'client_test',
            'password': 'MotDePasse#2026Solide',
            'email': 'client@test.ci',
            'nom': 'Kouassi',
            'prenom': 'Awa',
            'telephone': '+2250700000000',
            'zone': self.zone.pk,
            'point_eau_disponible': True,
        }

    def test_inscription_reussie_cree_utilisateur_et_client(self):
        reponse = self.client.post(self.url, self.payload_valide)
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Utilisateur.objects.filter(username='client_test').exists())
        client = Client.objects.get(utilisateur__username='client_test')
        self.assertEqual(client.zone, self.zone)
        self.assertTrue(client.point_eau_disponible)
        self.assertEqual(client.utilisateur.get_role(), 'client')

    def test_username_deja_pris_refuse(self):
        Utilisateur.objects.create_user(username='client_test', password='AutreMotDePasse#2026')
        reponse = self.client.post(self.url, self.payload_valide)
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', reponse.data)

    def test_zone_manquante_refusee(self):
        payload = {**self.payload_valide, 'username': 'autre_client'}
        del payload['zone']
        reponse = self.client.post(self.url, payload)
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('zone', reponse.data)

    def test_mot_de_passe_faible_refuse(self):
        payload = {**self.payload_valide, 'username': 'client_faible', 'password': '1234'}
        reponse = self.client.post(self.url, payload)
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', reponse.data)