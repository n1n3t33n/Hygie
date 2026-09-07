from .base import *
from .base import env

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# À activer une fois l'hébergeur choisi (08 Architecture, encore non tranché)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True