from rest_framework.permissions import BasePermission, DjangoModelPermissions


class IsClient(BasePermission):
    message = "Réservé aux comptes Client."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.get_role() == 'client'
        )


class IsAgent(BasePermission):
    """Tout profil Agent, agent_laveur comme chef_equipe (généralisation 07 UML)."""
    message = "Réservé aux comptes Agent."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.get_role() in ('agent', 'chef_equipe')
        )


class IsChefEquipe(BasePermission):
    message = "Réservé aux Chefs d'équipe."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.get_role() == 'chef_equipe'
        )


class IsAdministrateur(BasePermission):
    """Tout Administrateur, quelles que soient ses capacités précises."""
    message = "Réservé aux comptes Administrateur."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.get_role() == 'administrateur'
        )


class PermissionsModeleComplet(DjangoModelPermissions):
    """
    Étend DjangoModelPermissions (natif DRF) pour exiger explicitement
    "view_<modèle>" en lecture — par défaut, DRF n'exige aucune permission
    particulière pour GET/HEAD, seulement d'être authentifié. Utilisée sur
    les vues Agent et Client : le nom du modèle (et donc les permissions
    add_/change_/delete_/view_) est déduit automatiquement du queryset de
    la vue, donc une seule classe couvre les deux modèles.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class PeutModifierModele(BasePermission):
    """
    Exige "change_<modèle>" de la vue ciblée, indépendamment du verbe HTTP
    utilisé — pour des actions comme "désactiver" : sémantiquement une
    modification, même si elle passe par POST plutôt que PATCH.
    """
    message = "Vous n'avez pas la capacité de modifier ce compte."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            return False
        modele = queryset.model
        codename = f'{modele._meta.app_label}.change_{modele._meta.model_name}'
        return request.user.has_perm(codename)


class PeutCreerAdministrateur(BasePermission):
    """
    Capacité indivisible pour tout ce qui touche à un compte Administrateur
    (créer, lister, consulter, désactiver) — un Administrateur "limité" ne
    l'a pas par défaut. Choix délibéré de ne pas fragmenter cette capacité
    pour l'instant.
    """
    message = "Vous n'avez pas la capacité de gérer des comptes Administrateur."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.has_perm('comptes.creer_administrateur')
        )