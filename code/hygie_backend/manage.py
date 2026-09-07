#!/usr/bin/env python
"""Utilitaire en ligne de commande de Django pour les tâches d'administration."""
import os
import sys


def main():
    # En local, on utilise toujours "development" (PostgreSQL 16 local via DATABASE_URL, DEBUG=True)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hygie_backend.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Vérifie que (venv) apparaît bien "
            "au début de l'invite avant de relancer la commande."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()