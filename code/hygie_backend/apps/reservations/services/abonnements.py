"""
Règles de gestion de l'entité Abonnement (cas d'utilisation « Souscrire un abonnement »).

Décisions appliquées (validées le 18/10/2026, le 19/10/2026 et le 21/10/2026) :
  A1 — une fois créé, seul date_fin est modifiable (et doit rester >= date_debut) ;
  A2 — deux abonnements d'un même client ne peuvent pas se chevaucher. Les bornes sont
       INCLUSES : une période couvre tous les jours de date_debut à date_fin compris, et une
       date_fin vide signifie « sans fin ». Si l'ancien abonnement finit le 10, le suivant
       peut commencer le 11, pas le 10 ;
  date_debut >= aujourd'hui à la création (jour local d'Abidjan) ;
  aucune suppression : on met fin à un abonnement en renseignant date_fin ;
  raccourcir un abonnement qui a des réservations non annulées au-delà de la nouvelle fin
  exige l'accord explicite du demandeur : s'il accepte, ces réservations sont annulées ;
  s'il refuse, la date de fin n'est pas modifiée (la règle A3 reste toujours vraie).
"""
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.reservations.models import Abonnement

from . import reservations as service_reservations
from .exceptions import AnnulationAConfirmer, ErreurMetier
from .verrous import verrouiller_client


def _formater(date):
    return date.strftime('%d/%m/%Y')


def abonnements_accessibles(utilisateur):
    """
    Abonnements qu'un utilisateur a le droit de voir :
      - Client         : uniquement les siens ;
      - Administrateur : tous (l'accès effectif reste soumis aux permissions Django,
                         vérifiées par la couche API) ;
      - tout autre cas : aucun.
    """
    role = utilisateur.get_role()
    if role == 'client':
        return Abonnement.objects.filter(client=utilisateur.client)
    if role == 'administrateur':
        return Abonnement.objects.all()
    return Abonnement.objects.none()


def _verifier_non_chevauchement(client_pk, date_debut, date_fin, champ, exclure_pk=None):
    """
    A2, bornes incluses. Deux périodes [d1, f1] et [d2, f2] se chevauchent si
    d1 <= f2 ET d2 <= f1, une fin vide valant « sans fin ».
    """
    autres = Abonnement.objects.filter(client_id=client_pk)
    if exclure_pk is not None:
        autres = autres.exclude(pk=exclure_pk)
    if date_fin is not None:
        autres = autres.filter(date_debut__lte=date_fin)
    autres = autres.filter(Q(date_fin__isnull=True) | Q(date_fin__gte=date_debut))
    en_conflit = autres.order_by('date_debut').first()
    if en_conflit is not None:
        fin = _formater(en_conflit.date_fin) if en_conflit.date_fin else 'sans fin'
        raise ErreurMetier(
            "Cette période chevauche un autre abonnement de ce client "
            f"(du {_formater(en_conflit.date_debut)} au {fin}).",
            champ=champ,
        )


def creer_abonnement(*, client, frequence, date_debut, date_fin=None):
    if date_debut < timezone.localdate():
        raise ErreurMetier(
            "La date de début ne peut pas être antérieure à aujourd'hui.", champ='date_debut',
        )
    if date_fin is not None and date_fin < date_debut:
        raise ErreurMetier(
            "La date de fin ne peut pas être antérieure à la date de début.", champ='date_fin',
        )
    with transaction.atomic():
        verrouiller_client(client.pk)
        _verifier_non_chevauchement(client.pk, date_debut, date_fin, champ='date_debut')
        return Abonnement.objects.create(
            client=client, frequence=frequence, date_debut=date_debut, date_fin=date_fin,
        )


def _traiter_reservations_hors_periode(abonnement, nouvelle_fin, annuler_reservations,
                                       acteur_est_admin):
    """
    Réservations non annulées de l'abonnement situées après la nouvelle fin :
      - réponse absente -> AnnulationAConfirmer (on demande au demandeur) ;
      - réponse non     -> refus, rien n'est modifié ;
      - réponse oui     -> annulation de chacune ; si une seule ne peut pas être annulée
                           (ex. veille dépassée pour un Client, ou déjà terminée), tout est
                           refusé et rien n'est modifié.
    """
    concernees = service_reservations.reservations_apres_fin_abonnement(abonnement, nouvelle_fin)
    if not concernees:
        return
    nombre = len(concernees)
    pluriel = 's' if nombre > 1 else ''
    if annuler_reservations is None:
        raise AnnulationAConfirmer(
            f"{nombre} réservation{pluriel} de cet abonnement "
            f"{'sont prévues' if nombre > 1 else 'est prévue'} après le "
            f"{_formater(nouvelle_fin)}. Voulez-vous aussi {'les ' if nombre > 1 else 'l’'}annuler ?",
            concernees,
        )
    if annuler_reservations is False:
        raise ErreurMetier(
            f"La date de fin n'a pas été modifiée : {nombre} réservation{pluriel} "
            f"reste{'nt' if nombre > 1 else ''} prévue{pluriel} après le "
            f"{_formater(nouvelle_fin)} et vous avez choisi de ne pas {'les ' if nombre > 1 else 'l’'}annuler.",
            champ='date_fin',
        )
    for reservation in concernees:
        try:
            service_reservations.annuler_reservation(reservation, acteur_est_admin=acteur_est_admin)
        except ErreurMetier as erreur:
            raise ErreurMetier(
                "La date de fin n'a pas été modifiée : la réservation du "
                f"{_formater(reservation.date_reservation)} ({reservation.get_creneau_display()}) "
                f"ne peut pas être annulée. {erreur.message}",
                champ='date_fin',
            )


def modifier_date_fin(abonnement, date_fin, *, annuler_reservations=None, acteur_est_admin=False):
    """
    A1 : seule date_fin change. None est accepté (abonnement de nouveau sans fin) ; dans tous
    les cas la nouvelle période est revérifiée contre les autres abonnements du client, et
    les réservations rattachées qui sortiraient de la période sont traitées selon la réponse
    du demandeur (voir _traiter_reservations_hors_periode).
    """
    if date_fin is not None and date_fin < abonnement.date_debut:
        raise ErreurMetier(
            "La date de fin ne peut pas être antérieure à la date de début.", champ='date_fin',
        )
    if date_fin == abonnement.date_fin:
        return abonnement
    with transaction.atomic():
        verrouiller_client(abonnement.client_id)
        _verifier_non_chevauchement(
            abonnement.client_id, abonnement.date_debut, date_fin,
            champ='date_fin', exclure_pk=abonnement.pk,
        )
        if date_fin is not None:
            _traiter_reservations_hors_periode(
                abonnement, date_fin, annuler_reservations, acteur_est_admin,
            )
        abonnement.date_fin = date_fin
        abonnement.save(update_fields=['date_fin'])
    return abonnement