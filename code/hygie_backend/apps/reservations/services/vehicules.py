"""
Règles de gestion de l'entité Vehicule (cas d'utilisation « Ajouter un véhicule », P1 messages 5-8).

Décisions appliquées (validées le 18/10/2026) :
  V1 — immatriculation normalisée (espaces supprimés, majuscules, sans regex de format) et
       unique par client ;
  V2 — suppression refusée si le véhicule a des réservations.
"""
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from apps.reservations.models import Vehicule

from .exceptions import ErreurMetier

LONGUEUR_MAX_IMMATRICULATION = Vehicule._meta.get_field('immatriculation').max_length

MESSAGE_DOUBLON = "Vous avez déjà enregistré un véhicule avec cette immatriculation."
MESSAGE_SUPPRESSION_REFUSEE = (
    "Ce véhicule est lié à des réservations : il ne peut pas être supprimé."
)


def normaliser_immatriculation(valeur):
    """
    Supprime tous les espaces (y compris tabulations et espaces insécables) et met en
    majuscules. Les tirets sont conservés. Aucun format national n'est imposé.
    """
    return ''.join(str(valeur).split()).upper()


def valider_immatriculation(valeur):
    """Retourne l'immatriculation normalisée, ou lève ErreurMetier si elle est inutilisable."""
    normalisee = normaliser_immatriculation(valeur)
    if not normalisee:
        raise ErreurMetier("L'immatriculation ne peut pas être vide.", champ='immatriculation')
    if len(normalisee) > LONGUEUR_MAX_IMMATRICULATION:
        raise ErreurMetier(
            f"L'immatriculation ne peut pas dépasser {LONGUEUR_MAX_IMMATRICULATION} caractères.",
            champ='immatriculation',
        )
    return normalisee


def vehicules_accessibles(utilisateur):
    """
    Véhicules qu'un utilisateur a le droit de voir :
      - Client         : uniquement les siens ;
      - Administrateur : tous (l'accès effectif reste soumis à la permission view_vehicule,
                         vérifiée par la couche API) ;
      - tout autre cas : aucun.
    """
    role = utilisateur.get_role()
    if role == 'client':
        return Vehicule.objects.filter(client=utilisateur.client)
    if role == 'administrateur':
        return Vehicule.objects.all()
    return Vehicule.objects.none()


def _verifier_unicite(client, immatriculation, exclure_pk=None):
    doublons = Vehicule.objects.filter(client=client, immatriculation=immatriculation)
    if exclure_pk is not None:
        doublons = doublons.exclude(pk=exclure_pk)
    if doublons.exists():
        raise ErreurMetier(MESSAGE_DOUBLON, champ='immatriculation')


def creer_vehicule(*, client, immatriculation, type_vehicule):
    """P1 message 6 : create(immatriculation, typeVehicule, idClient)."""
    immatriculation = valider_immatriculation(immatriculation)
    _verifier_unicite(client, immatriculation)
    try:
        # Savepoint : une collision concurrente (deux requêtes simultanées) est rattrapée
        # ici, et la transaction englobante reste utilisable.
        with transaction.atomic():
            return Vehicule.objects.create(
                client=client,
                immatriculation=immatriculation,
                type_vehicule=type_vehicule,
            )
    except IntegrityError:
        raise ErreurMetier(MESSAGE_DOUBLON, champ='immatriculation')


def modifier_vehicule(vehicule, *, immatriculation=None, type_vehicule=None):
    """Met à jour les seuls champs fournis. Le propriétaire (client) ne change jamais."""
    champs = []
    if immatriculation is not None:
        immatriculation = valider_immatriculation(immatriculation)
        if immatriculation != vehicule.immatriculation:
            _verifier_unicite(vehicule.client, immatriculation, exclure_pk=vehicule.pk)
            vehicule.immatriculation = immatriculation
            champs.append('immatriculation')
    if type_vehicule is not None and type_vehicule != vehicule.type_vehicule:
        vehicule.type_vehicule = type_vehicule
        champs.append('type_vehicule')
    if champs:
        try:
            with transaction.atomic():
                vehicule.save(update_fields=champs)
        except IntegrityError:
            raise ErreurMetier(MESSAGE_DOUBLON, champ='immatriculation')
    return vehicule


def supprimer_vehicule(vehicule):
    """V2 : refuse si des réservations référencent ce véhicule (clé étrangère PROTECT)."""
    if vehicule.reservations.exists():
        raise ErreurMetier(MESSAGE_SUPPRESSION_REFUSEE)
    try:
        vehicule.delete()
    except ProtectedError:
        # Réservation créée entre la vérification et la suppression.
        raise ErreurMetier(MESSAGE_SUPPRESSION_REFUSEE)