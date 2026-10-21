from rest_framework.permissions import SAFE_METHODS, BasePermission


class PeutGererVehicules(BasePermission):
    """
    Accès à l'API Véhicule (décision V3, validée le 18/10/2026) :
      - Client         : CRUD complet, limité à ses propres véhicules (le filtrage est fait
                         par services.vehicules.vehicules_accessibles) ;
      - Administrateur : lecture seule, et uniquement avec la capacité Django native
                         reservations.view_vehicule (groupe « Administrateur - Consulter les
                         véhicules ») — le superuser l'a d'office ;
      - Agent / Chef d'équipe / compte sans profil : aucun accès.
    """
    message = (
        "Seuls les Clients gèrent leurs véhicules ; les Administrateurs habilités "
        "y ont un accès en lecture seule."
    )

    def has_permission(self, request, view):
        utilisateur = request.user
        if not (utilisateur and utilisateur.is_authenticated):
            return False
        role = utilisateur.get_role()
        if role == 'client':
            return True
        if role == 'administrateur':
            return (
                request.method in SAFE_METHODS
                and utilisateur.has_perm('reservations.view_vehicule')
            )
        return False


class PeutGererAbonnements(BasePermission):
    """
    Accès à l'API Abonnement (décision du 19/10/2026) :
      - Client         : liste, souscription, détail et fin de ses propres abonnements ;
      - Administrateur : mêmes actions sur tous les abonnements, mais chaque action exige la
                         permission Django native correspondante (groupe « Administrateur -
                         Gérer les abonnements ») : view_abonnement, add_abonnement ou
                         change_abonnement — le superuser les a d'office ;
      - Agent / Chef d'équipe / compte sans profil : aucun accès.
    La suppression n'existe pour personne.
    """
    message = (
        "Seuls les Clients et les Administrateurs habilités peuvent accéder aux abonnements."
    )

    PERMISSION_PAR_METHODE = {
        'GET': 'reservations.view_abonnement',
        'HEAD': 'reservations.view_abonnement',
        'OPTIONS': 'reservations.view_abonnement',
        'POST': 'reservations.add_abonnement',
        'PUT': 'reservations.change_abonnement',
        'PATCH': 'reservations.change_abonnement',
    }

    def has_permission(self, request, view):
        utilisateur = request.user
        if not (utilisateur and utilisateur.is_authenticated):
            return False
        # Méthode que la vue n'expose pas (ex. DELETE) : on laisse DRF répondre 405 de la même
        # façon pour tous les rôles autorisés, plutôt qu'un 403 pour les uns et un 405 pour les autres.
        if request.method.lower() not in view.http_method_names:
            return utilisateur.get_role() in ('client', 'administrateur')
        role = utilisateur.get_role()
        if role == 'client':
            return True
        if role == 'administrateur':
            permission = self.PERMISSION_PAR_METHODE.get(request.method)
            return permission is not None and utilisateur.has_perm(permission)
        return False


class PeutGererReservations(BasePermission):
    """
    Accès à l'API Réservation (décision R2, validée le 18/10/2026). Chaque vue déclare son
    action dans `action_reservation` :
      - consulter  : Client (les siennes) ; Administrateur avec view_reservation (toutes) ;
      - creer      : Client uniquement — jamais l'Administrateur, même superuser, car une
                     réservation appartient à un Client ;
      - annuler    : Client (les siennes, jusqu'à la veille) ; Administrateur avec
                     change_reservation (à tout moment avant « terminée ») ;
      - administrer (confirmer, terminer) : Administrateur avec change_reservation uniquement.
    Les permissions viennent du groupe « Administrateur - Gérer les réservations » ; le
    superuser les a d'office. Agent / Chef d'équipe / compte sans profil : aucun accès
    (l'accès du Chef d'équipe sera traité à l'étape missions).
    """
    message = "Vous n'avez pas le droit d'effectuer cette action sur les réservations."

    def has_permission(self, request, view):
        utilisateur = request.user
        if not (utilisateur and utilisateur.is_authenticated):
            return False
        action = getattr(view, 'action_reservation', None)
        role = utilisateur.get_role()
        if action == 'creer':
            return role == 'client'
        if action == 'consulter':
            return role == 'client' or (
                role == 'administrateur' and utilisateur.has_perm('reservations.view_reservation')
            )
        if action == 'annuler':
            return role == 'client' or (
                role == 'administrateur' and utilisateur.has_perm('reservations.change_reservation')
            )
        if action == 'administrer':
            return role == 'administrateur' and utilisateur.has_perm(
                'reservations.change_reservation'
            )
        return False