"""
ASGI config for hygie_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

"""Point d'entrée ASGI, nécessaire plus tard pour Django Channels (WebSockets/chat)."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hygie_backend.settings.production')

application = get_asgi_application()