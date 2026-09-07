from .base import *
from .base import env

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': env.db('DATABASE_URL')
}