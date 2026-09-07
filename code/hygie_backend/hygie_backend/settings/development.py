"""Réglages actifs quand tu lances `python manage.py runserver` en local."""
from .base import *
from .base import env   # réimport explicite : rend la dépendance à "env" lisible malgré l'import *

# Lu directement depuis .env (DEBUG=True) plutôt que codé en dur, pour rester cohérent
# avec la valeur réellement présente dans le fichier .env.
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': env.db('DATABASE_URL')   # lit DATABASE_URL=postgres://... dans .env
}