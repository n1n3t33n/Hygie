"""
Réglages Django communs à TOUS les environnements (dev et prod).
Les valeurs qui changent selon l'environnement (base de données, DEBUG, hôtes autorisés)
sont dans development.py / production.py, jamais ici.
"""
from pathlib import Path
import environ

# __file__ = .../hygie_backend/hygie_backend/settings/base.py
# .parent      -> settings/
# .parent.parent -> hygie_backend/ (paquet de config)
# .parent.parent.parent -> hygie_backend/ (racine du projet, contient manage.py et .env)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lit le fichier .env situé à la racine du projet (à côté de manage.py)
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')

# --- Apps Django natives ---
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# --- Bibliothèques tierces ---
THIRD_PARTY_APPS = [
    'rest_framework',          # Django REST Framework
    'drf_spectacular',         # Génération Swagger/Redoc
    'corsheaders',             # Autorise les appels cross-origin (Flutter, futur back-office Next.js)
    'rest_framework_simplejwt.token_blacklist',
]

# --- Nos 5 apps métier, regroupées dans le dossier apps/ ---
LOCAL_APPS = [
    'apps.comptes',
    'apps.reservations',
    'apps.paiements',
    'apps.missions',
    'apps.evaluations',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',   # doit être avant CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hygie_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hygie_backend.wsgi.application'
ASGI_APPLICATION = 'hygie_backend.asgi.application'

# --- Authentification ---
# Modèle unique (AbstractUser), décidé le : profils Client/Agent viendront en OneToOne dessus.
AUTH_USER_MODEL = 'comptes.Utilisateur'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalisation ---
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Abidjan'   # fuseau horaire d'Abidjan, cohérent avec RG3 (créneaux 4h-6h30 / 20h-00h)
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'   # cohérent avec BigInt PK du MPD

# --- Django REST Framework + JWT ---
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'TOKEN_OBTAIN_SERIALIZER': 'apps.comptes.serializers.UtilisateurTokenObtainPairSerializer', # est un point d'extension natif de simplejwt : il permet à TokenObtainPairView d'utiliser directement notre serializer personnalisé sans avoir besoin de sous-classer la vue.
    
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Hygie Sanitaire API',
    'DESCRIPTION': "API du service de lavage automobile à domicile Hygie Sanitaire",
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# --- CORS (Flutter mobile + futur back-office Next.js) ---
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'