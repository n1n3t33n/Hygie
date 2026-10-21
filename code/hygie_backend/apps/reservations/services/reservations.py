"""
Règles de gestion de l'entité Reservation (cas d'utilisation « Réserver un lavage »).

Décisions appliquées (validées le 18/10/2026 et le 21/10/2026) :
  RG1 — réservation refusée si le client n'a pas de point d'eau disponible ;
  R1  — date_reservation >= demain (DELAI_MINIMUM_JOURS), sans horizon maximum ;
  RG5 — le véhicule est facultatif ; s'il est fourni, il appartient au client ;
  A3  — une réservation rattachée à un abonnement : même client, date dans la période de
        l'abonnement (bornes incluses, date_fin vide = sans fin) ;
  RG6 — un client n'a qu'une réservation non annulée par couple (date, créneau) ;
  une réservation est toujours créée « en attente » ;
  RG4 — le Client annule jusqu'à la veille incluse ; l'Administrateur annule à tout moment
        avant « terminée » ;
  confirmer : en attente -> confirmée, au plus tard le jour de la réservation (une réservation
  dont la date est dépassée ne se confirme plus) ; terminer : confirmée -> terminée, dès le
  jour de la réservation ; aucune modification après création (on annule puis on recrée) ;
  expiration (21/10/2026) : une réservation encore « en attente » le lendemain de sa date est
  annulée automatiquement, avec le motif « expiration » ; les réservations confirmées ou
  terminées ne sont jamais touchées. Chaque annulation enregistre son motif (client,
  administrateur ou expiration).

Les dates sont comparées en jour local (Africa/Abidjan). Pour le créneau du soir,
date_reservation est le jour où le créneau commence.
"""
import datetime

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.reservations.models import MotifAnnulation, Reservation, StatutReservation

from .exceptions import ErreurMetier
from .verrous import verrouiller_client

DELAI_MINIMUM_JOURS = 1            # R1 : réservation au plus tôt demain
DELAI_ANNULATION_CLIENT_JOURS = 1  # RG4 : le Client annule au plus tard la veille

MESSAGE_CRENEAU_PRIS = (
    "Vous avez déjà une réservation à cette date sur ce créneau. "
    "Annulez-la d'abord ou choisissez un autre créneau."
)


def _formater(date):
    return date.strftime('%d/%m/%Y')


def reservations_accessibles(utilisateur):
    """
    Réservations qu'un utilisateur a le droit de voir :
      - Client         : uniquement les siennes ;
      - Administrateur : toutes (l'accès effectif reste soumis aux permissions Django,
                         vérifiées par la couche API) ;
      - tout autre cas : aucune.
    """
    role = utilisateur.get_role()
    if role == 'client':
        return Reservation.objects.filter(client=utilisateur.client)
    if role == 'administrateur':
        return Reservation.objects.all()
    return Reservation.objects.none()


def _verifier_abonnement(client, abonnement, date_reservation):
    """A3, sur la version la plus récente de l'abonnement (relu sous verrou)."""
    abonnement.refresh_from_db()
    if abonnement.client_id != client.pk:
        raise ErreurMetier("Cet abonnement ne vous appartient pas.", champ='abonnement')
    fin = abonnement.date_fin
    if date_reservation < abonnement.date_debut or (fin is not None and date_reservation > fin):
        periode = (
            f"du {_formater(abonnement.date_debut)} au {_formater(fin)}"
            if fin else f"à partir du {_formater(abonnement.date_debut)}"
        )
        raise ErreurMetier(
            f"La date choisie est hors de la période de cet abonnement ({periode}).",
            champ='abonnement',
        )


def creer_reservation(*, client, date_reservation, creneau, vehicule=None, abonnement=None):
    if not client.point_eau_disponible:
        raise ErreurMetier(
            "Réservation impossible : aucun point d'eau n'est disponible à votre adresse."
        )
    premiere_date = timezone.localdate() + datetime.timedelta(days=DELAI_MINIMUM_JOURS)
    if date_reservation < premiere_date:
        raise ErreurMetier(
            f"La date de réservation doit être au plus tôt le {_formater(premiere_date)}.",
            champ='date_reservation',
        )
    if vehicule is not None and vehicule.client_id != client.pk:
        raise ErreurMetier("Ce véhicule ne vous appartient pas.", champ='vehicule')

    with transaction.atomic():
        verrouiller_client(client.pk)
        if abonnement is not None:
            _verifier_abonnement(client, abonnement, date_reservation)
        deja_prise = Reservation.objects.filter(
            client=client, date_reservation=date_reservation, creneau=creneau,
        ).exclude(statut=StatutReservation.ANNULEE).exists()
        if deja_prise:
            raise ErreurMetier(MESSAGE_CRENEAU_PRIS, champ='creneau')
        try:
            # Savepoint : une collision rattrapée par la contrainte en base laisse la
            # transaction englobante utilisable.
            with transaction.atomic():
                return Reservation.objects.create(
                    client=client,
                    date_reservation=date_reservation,
                    creneau=creneau,
                    statut=StatutReservation.EN_ATTENTE,
                    vehicule=vehicule,
                    abonnement=abonnement,
                )
        except IntegrityError:
            raise ErreurMetier(MESSAGE_CRENEAU_PRIS, champ='creneau')


def _relire_verrouillee(reservation):
    return Reservation.objects.select_for_update().get(pk=reservation.pk)


def annuler_reservation(reservation, *, acteur_est_admin=False):
    """RG4 : le Client jusqu'à la veille incluse ; l'Administrateur jusqu'à « terminée »."""
    with transaction.atomic():
        courante = _relire_verrouillee(reservation)
        if courante.statut == StatutReservation.ANNULEE:
            raise ErreurMetier("Cette réservation est déjà annulée.")
        if courante.statut == StatutReservation.TERMINEE:
            raise ErreurMetier("Une réservation terminée ne peut plus être annulée.")
        if not acteur_est_admin:
            derniere_date = courante.date_reservation - datetime.timedelta(
                days=DELAI_ANNULATION_CLIENT_JOURS
            )
            if timezone.localdate() > derniere_date:
                raise ErreurMetier(
                    "L'annulation n'est possible que jusqu'à la veille de la réservation "
                    f"(au plus tard le {_formater(derniere_date)})."
                )
        courante.statut = StatutReservation.ANNULEE
        courante.motif_annulation = (
            MotifAnnulation.ADMINISTRATEUR if acteur_est_admin else MotifAnnulation.CLIENT
        )
        courante.save(update_fields=['statut', 'motif_annulation'])
    reservation.statut = courante.statut
    reservation.motif_annulation = courante.motif_annulation
    return reservation


def confirmer_reservation(reservation):
    """
    en attente -> confirmée, au plus tard le jour de la réservation. Appelée par
    l'Administrateur, plus tard aussi par paiements.
    """
    with transaction.atomic():
        courante = _relire_verrouillee(reservation)
        if courante.statut != StatutReservation.EN_ATTENTE:
            raise ErreurMetier(
                "Seule une réservation en attente peut être confirmée "
                f"(statut actuel : {courante.get_statut_display().lower()})."
            )
        if timezone.localdate() > courante.date_reservation:
            raise ErreurMetier(
                "Cette réservation ne peut plus être confirmée : sa date "
                f"({_formater(courante.date_reservation)}) est dépassée."
            )
        courante.statut = StatutReservation.CONFIRMEE
        courante.save(update_fields=['statut'])
    reservation.statut = StatutReservation.CONFIRMEE
    return reservation


def terminer_reservation(reservation):
    """confirmée -> terminée, au plus tôt le jour de la réservation."""
    with transaction.atomic():
        courante = _relire_verrouillee(reservation)
        if courante.statut != StatutReservation.CONFIRMEE:
            raise ErreurMetier(
                "Seule une réservation confirmée peut être terminée "
                f"(statut actuel : {courante.get_statut_display().lower()})."
            )
        if timezone.localdate() < courante.date_reservation:
            raise ErreurMetier(
                "Cette réservation ne peut pas être terminée avant le jour prévu "
                f"({_formater(courante.date_reservation)})."
            )
        courante.statut = StatutReservation.TERMINEE
        courante.save(update_fields=['statut'])
    reservation.statut = StatutReservation.TERMINEE
    return reservation


def reservations_echues():
    """
    Réservations à expirer : encore « en attente » alors que leur date est passée (on est
    au moins le lendemain). Cohérent avec confirmer_reservation, qui accepte jusqu'au jour
    de la réservation inclus : une réservation en attente est donc soit confirmable, soit
    à expirer, sans zone grise. Les réservations confirmées ne sont jamais concernées.
    """
    return Reservation.objects.filter(
        statut=StatutReservation.EN_ATTENTE, date_reservation__lt=timezone.localdate(),
    )


def expirer_reservations_echues():
    """
    Annule les réservations échues non traitées, avec le motif « expiration », et retourne
    leur nombre. Idempotente : relancée, elle ne trouve plus rien. Un seul UPDATE : si un
    administrateur confirme une réservation au même instant, PostgreSQL réévalue la
    condition une fois son verrou levé et la laisse confirmée. Destinée à être appelée par
    un planificateur (voir la commande de gestion `expirer_reservations`).
    """
    return reservations_echues().update(
        statut=StatutReservation.ANNULEE, motif_annulation=MotifAnnulation.EXPIRATION,
    )


def reservations_apres_fin_abonnement(abonnement, nouvelle_fin):
    """Réservations non annulées de l'abonnement dont la date dépasse la nouvelle fin (A3)."""
    return list(
        Reservation.objects.filter(abonnement=abonnement, date_reservation__gt=nouvelle_fin)
        .exclude(statut=StatutReservation.ANNULEE)
        .order_by('date_reservation', 'creneau', 'id_reservation')
    )