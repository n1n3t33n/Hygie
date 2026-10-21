from rest_framework import serializers

from apps.comptes.models import Client
from apps.reservations.api_erreurs import ConfirmationRequise
from apps.reservations.models import Abonnement
from apps.reservations.services import abonnements as service_abonnements
from apps.reservations.services.exceptions import AnnulationAConfirmer, ErreurMetier


def _en_erreur_de_validation(erreur):
    """Traduit une ErreurMetier du service en erreur 400 DRF, rattachée à son champ."""
    if erreur.champ:
        return serializers.ValidationError({erreur.champ: [erreur.message]})
    return serializers.ValidationError(erreur.message)


class AbonnementSerializer(serializers.ModelSerializer):
    """
    Lecture et création d'un abonnement. Aucune règle métier ici : elles vivent dans
    services/abonnements.py.

    Le propriétaire dépend du rôle de l'appelant :
      - Client         : toujours lui-même, le champ « client » du corps est ignoré ;
      - Administrateur : le champ « client » est obligatoire (il crée pour un client).
    """
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)

    class Meta:
        model = Abonnement
        fields = ['id_abonnement', 'frequence', 'date_debut', 'date_fin', 'client']
        read_only_fields = ['id_abonnement']

    def validate(self, attrs):
        # Création uniquement : la modification passe par AbonnementFinSerializer.
        utilisateur = self.context['request'].user
        if utilisateur.get_role() == 'client':
            attrs['client'] = utilisateur.client
        elif 'client' not in attrs:
            raise serializers.ValidationError(
                {'client': ["Ce champ est obligatoire pour un administrateur."]}
            )
        return attrs

    def create(self, validated_data):
        try:
            return service_abonnements.creer_abonnement(**validated_data)
        except ErreurMetier as erreur:
            raise _en_erreur_de_validation(erreur)


class AbonnementFinSerializer(serializers.ModelSerializer):
    """
    Modification d'un abonnement (règle A1) : seuls date_fin et, en réponse à la question
    posée par l'API, annuler_reservations peuvent être envoyés. Tout autre champ est refusé
    explicitement plutôt qu'ignoré en silence.

    annuler_reservations (facultatif, jamais renvoyé) : si le raccourcissement laisse des
    réservations au-delà de la nouvelle fin, l'API répond 409 « confirmation_requise » avec la
    liste ; le demandeur renvoie alors la même requête avec true (annuler aussi ces
    réservations) ou false (renoncer à raccourcir).
    """
    annuler_reservations = serializers.BooleanField(
        required=False, allow_null=True, write_only=True,
    )

    class Meta:
        model = Abonnement
        fields = [
            'id_abonnement', 'frequence', 'date_debut', 'date_fin', 'client',
            'annuler_reservations',
        ]
        read_only_fields = ['id_abonnement', 'frequence', 'date_debut', 'client']

    def validate(self, attrs):
        interdits = set(self.initial_data) - {'date_fin', 'annuler_reservations'}
        if interdits:
            raise serializers.ValidationError({
                champ: ["Ce champ n'est pas modifiable : seule la date de fin peut l'être."]
                for champ in sorted(interdits)
            })
        return attrs

    def update(self, instance, validated_data):
        if 'date_fin' not in validated_data:
            return instance
        utilisateur = self.context['request'].user
        try:
            return service_abonnements.modifier_date_fin(
                instance,
                validated_data['date_fin'],
                annuler_reservations=validated_data.get('annuler_reservations'),
                acteur_est_admin=utilisateur.get_role() == 'administrateur',
            )
        except AnnulationAConfirmer as question:
            raise ConfirmationRequise(
                question.message,
                [
                    {
                        'id_reservation': r.id_reservation,
                        'date_reservation': r.date_reservation.isoformat(),
                        'creneau': r.creneau,
                        'statut': r.statut,
                    }
                    for r in question.reservations
                ],
                champ_reponse='annuler_reservations',
            )
        except ErreurMetier as erreur:
            raise _en_erreur_de_validation(erreur)