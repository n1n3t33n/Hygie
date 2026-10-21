from django.core.management.base import BaseCommand

from apps.reservations.services import reservations as service_reservations


class Command(BaseCommand):
    help = (
        "Annule les réservations encore « en attente » dont la date est dépassée "
        "(motif « expiration »). Sans danger à relancer : à planifier une fois par jour, "
        "de préférence après minuit, heure d'Abidjan."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Affiche combien de réservations seraient annulées, sans rien modifier.",
        )

    def handle(self, *args, **options):
        # Aucune règle ici : la commande ne fait qu'appeler le service et afficher le résultat.
        if options['dry_run']:
            nombre = service_reservations.reservations_echues().count()
            self.stdout.write(f"{nombre} réservation(s) seraient annulées (simulation, rien modifié).")
            return
        nombre = service_reservations.expirer_reservations_echues()
        self.stdout.write(self.style.SUCCESS(f"{nombre} réservation(s) expirée(s) et annulée(s)."))