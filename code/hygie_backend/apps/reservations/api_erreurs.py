from rest_framework import status
from rest_framework.exceptions import APIException


class ConflitMetier(APIException):
    """409 : l'opération est refusée à cause de l'état actuel des données (ex. suppression)."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Opération impossible dans l'état actuel des données."
    default_code = 'conflit'


class ConfirmationRequise(APIException):
    """
    409 : l'opération entraînerait l'annulation de réservations. La réponse liste ces
    réservations et indique le champ à renvoyer (true pour accepter, false pour refuser).

    DRF convertirait tout le contenu d'une exception en texte : le corps de la réponse est
    donc construit par la vue à partir de `payload`, qui garde les nombres tels quels.
    """
    status_code = status.HTTP_409_CONFLICT
    default_code = 'confirmation_requise'

    def __init__(self, message, reservations, champ_reponse):
        super().__init__(detail=message)
        self.payload = {
            'detail': message,
            'code': self.default_code,
            'champ_reponse': champ_reponse,
            'reservations': reservations,
        }