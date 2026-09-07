"""
WSGI config for hygie_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

"""Point d'entrée WSGI, utilisé uniquement en déploiement (pas par runserver)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hygie_backend.settings.production')

application = get_wsgi_application()