"""
Réglages de production — pas encore utilisés (hébergeur non choisi, voir 08 Architecture).
DEBUG reste codé en dur à False ici, volontairement, même si .env venait à contenir DEBUG=True :
en production, on ne veut jamais dépendre d'une variable d'environnement mal configurée.
"""
from .base import *
from .base import env

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': env.db('DATABASE_URL')
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True