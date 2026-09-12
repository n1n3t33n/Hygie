from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UtilisateurTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Ajoute des informations de base dans le payload du token JWT,
    pour éviter un appel API supplémentaire côté mobile/back-office
    juste après la connexion.

    role : calculé via Utilisateur.get_role() ('client' / 'agent' / 'chef_equipe' /
    'administrateur' / None), maintenant que le lien OneToOne Utilisateur <->
    Client/Agent/Administrateur est confirmé.

    TODO: id_zone / id_agent / id_client — décision distincte, non traitée ici
    (voir remarque de fin de réponse).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['role'] = user.get_role()
        return token