from django.contrib.auth.password_validation import validate_password as _valider_politique_mdp
from rest_framework import serializers

from apps.comptes.models.utilisateur import Utilisateur


class CompteMixin(serializers.Serializer):
    """
    Champs d'authentification communs à toute création de compte (Client,
    Agent, Administrateur) — portés par Utilisateur, pas par le profil
    métier. Centralise la validation d'unicité du username et la création
    de l'Utilisateur, pour que les trois serializers restent cohérents.

    Ces 4 champs sont en write_only : Client/Agent/Administrateur n'ont pas
    ces attributs directement (ils vivent sur instance.utilisateur), donc
    DRF ne peut pas les relire automatiquement sur l'objet retourné par
    create(). to_representation() les réinjecte manuellement en lecture.

    Exclusivité des profils garantie par construction : ce mixin ne crée
    JAMAIS de profil sur un Utilisateur existant, uniquement sur un
    Utilisateur fraîchement créé dans le même appel.
    """
    username = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, default='', write_only=True)
    nom = serializers.CharField(max_length=150, write_only=True)
    prenom = serializers.CharField(max_length=150, write_only=True)

    def validate_username(self, value):
        if Utilisateur.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_password(self, value):
        _valider_politique_mdp(value)
        return value

    def _creer_utilisateur(self, validated_data):
        """Retire les champs d'authentification de validated_data et crée l'Utilisateur."""
        return Utilisateur.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email', ''),
            password=validated_data.pop('password'),
            last_name=validated_data.pop('nom'),
            first_name=validated_data.pop('prenom'),
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = instance.utilisateur.username
        data['email'] = instance.utilisateur.email
        data['nom'] = instance.utilisateur.last_name
        data['prenom'] = instance.utilisateur.first_name
        return data

class ProfilDetailMixin(serializers.Serializer):
    """
    Champs d'authentification en lecture seule pour les serializers de
    consultation/modification d'un profil déjà existant (liste, détail,
    PATCH) — symétrique à CompteMixin, mais on n'autorise pas de changer
    username/email/nom/prénom via ces vues (hors périmètre de cette étape).
    """
    username = serializers.CharField(source='utilisateur.username', read_only=True)
    email = serializers.EmailField(source='utilisateur.email', read_only=True)
    nom = serializers.CharField(source='utilisateur.last_name', read_only=True)
    prenom = serializers.CharField(source='utilisateur.first_name', read_only=True)
    is_active = serializers.BooleanField(source='utilisateur.is_active', read_only=True)