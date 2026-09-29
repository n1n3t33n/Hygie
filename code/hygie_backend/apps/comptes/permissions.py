from rest_framework.permissions import BasePermission


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


class PeutGererUtilisateurs(BasePermission):
    """
    Capacité "Gérer les utilisateurs" (07 UML) — ici, création de comptes
    Agent. Accordée automatiquement à un superuser ; pour un Administrateur
    limité, doit être explicitement assignée via la permission Django
    "comptes.add_agent" (générée automatiquement par Django pour le modèle
    Agent, assignable via un Group).
    """
    message = "Vous n'avez pas la capacité de gérer les utilisateurs."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.has_perm('comptes.add_agent')
        )


class PeutCreerAdministrateur(BasePermission):
    """
    Capacité distincte du simple rôle Administrateur : un Administrateur
    "limité" (créé pour un lavage partenaire) ne l'a pas par défaut.
    """
    message = "Vous n'avez pas la capacité de créer des comptes Administrateur."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.has_perm('comptes.creer_administrateur')
        )