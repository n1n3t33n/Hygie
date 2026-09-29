# apps/comptes/apps.py
from django.apps import AppConfig


class ComptesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.comptes'

    def ready(self):
        import apps.comptes.signals  # noqa: F401 — nécessaire pour enregistrer le récepteur du signal