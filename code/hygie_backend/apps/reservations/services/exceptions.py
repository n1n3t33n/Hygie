class ErreurMetier(Exception):
    """
    Violation d'une règle de gestion détectée dans services/.

    Les services ne connaissent ni HTTP ni DRF (convention 09 Backend Django : aucune
    logique métier dans les views). Ils lèvent cette exception ; la couche API (serializers
    et views) la traduit en réponse HTTP.

    champ : nom du champ fautif si l'erreur lui est rattachée (-> 400 sur ce champ),
            None sinon (-> traitée comme un conflit d'état, ex. suppression refusée).
    """

    def __init__(self, message, champ=None):
        super().__init__(message)
        self.message = message
        self.champ = champ


class AnnulationAConfirmer(ErreurMetier):
    """
    L'opération demandée entraînerait l'annulation de réservations : il faut d'abord
    l'accord explicite du demandeur. `reservations` liste celles qui seraient annulées.
    """

    def __init__(self, message, reservations):
        super().__init__(message)
        self.reservations = list(reservations)