from apps.comptes.models import Client


def verrouiller_client(client_pk):
    """
    Verrouille la ligne du client jusqu'à la fin de la transaction en cours : les opérations
    simultanées d'un même client (souscrire, réserver, raccourcir un abonnement) sont ainsi
    traitées l'une après l'autre, et leurs vérifications ne peuvent pas être contournées par
    une course. À appeler dans transaction.atomic(). Sans effet sous SQLite.
    """
    list(Client.objects.select_for_update().filter(pk=client_pk))