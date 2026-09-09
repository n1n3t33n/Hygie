from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UtilisateurTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Ajoute des informations de base dans le payload du token JWT,
    pour éviter un appel API supplémentaire côté mobile/back-office
    juste après la connexion.

    Limité pour l'instant aux champs déjà présents sur Utilisateur (AbstractUser).
    TODO: ajouter role / id_zone / id_agent / id_client une fois le lien
    OneToOne Utilisateur <-> Client/Agent et le rôle métier confirmés.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        return token