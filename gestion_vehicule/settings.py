import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from decouple import config
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = "fr"

LANGUAGES = [
    ("fr", _("Français")),
    ("en", _("English")),
    ("ht", _("Kreyòl Ayisyen")),
]

BSCSCAN_API_KEY = config('BSCSCAN_API_KEY')

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète pour Django, à ne pas exposer dans les environnements de production
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")

# Activation ou non du mode debug (ne pas laisser True en production)
DEBUG = os.getenv("DEBUG", "True") == "True"

# Liste des hôtes autorisés pour les requêtes
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Personnalisation du modèle utilisateur
AUTH_USER_MODEL = "users.CustomUser"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.staticfiles",

    "users.apps.UsersConfig",
    "core.apps.CoreConfig",
    "contracts.apps.ContractsConfig",
    "payments.apps.PaymentsConfig",
    "vehicles.apps.VehiclesConfig",
    "tolls.apps.TollsConfig",
    "otp.apps.OtpConfig",
    "fines.apps.FinesConfig",
    "documents.apps.DocumentsConfig",

    "widget_tweaks",
    "rest_framework",
    "crispy_forms",
    "crispy_tailwind",

    "notifications.apps.NotificationsConfig",  # ✅ TRÈS IMPORTANT
    "corsheaders",
    "django_filters",
    "django_extensions",
    "channels",
    "django_celery_beat",
    "twilio",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ["tailwind", "bootstrap4", "bootstrap5"]
CRISPY_TEMPLATE_PACK = "tailwind"  # ou "bootstrap4" selon ce que tu veux
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    #"users.middleware.VerifiedAccountMiddleware",
    "users.middleware.AccountLockMiddleware",       # Middleware pour verrouiller un compte après trop de tentatives
    "users.middleware.GeolocationLoggingMiddleware", 
   # "debug_toolbar.middleware.DebugToolbarMiddleware", # Middleware pour enregistrer la géolocalisation
    "users.middleware.SecurityMiddleware",           # Middleware pour des vérifications de sécurité supplémentaires
]

ROOT_URLCONF = "gestion_vehicule.urls"

# Configuration des fichiers statiques (CSS, JS, images, etc.)
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Configuration des fichiers médias (upload d'images, documents, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuration des templates HTML
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Chemins des répertoires de templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Configuration pour WSGI (utilisé en production)
WSGI_APPLICATION = "gestion_vehicule.wsgi.application"

# Configuration pour ASGI (utilisé pour WebSockets avec Channels)
ASGI_APPLICATION = "gestion_vehicule.asgi.application"

# Base de données SQLite (peut être remplacée par PostgreSQL en production)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    },
    'archive': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "archive.sqlite3",
    }
}

DATABASE_ROUTERS = ['gestion_vehicule.db_router.DeletedFineRouter']

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Validateurs de mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Paramètres de localisation
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True
USE_L10N = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuration de l'email pour envoyer des emails (ex : récupération de mot de passe, notifications)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "no-reply@jeremachinou.com"
SERVER_EMAIL = "no-reply@jeremachinou.com"

# Paramètres de sécurité
SECURE_SSL_REDIRECT = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Redirections après connexion/déconnexion
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/otp/generate-otp/"
LOGOUT_REDIRECT_URL = "login"

# Authentification avec plusieurs backends : Auth standard + Email + OTP
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Backend standard
    "users.backends.EmailAuthBackend",           # Backend personnalisé basé sur l'email
    "users.backends.OTPAuthBackend",             # Backend personnalisé basé sur OTP
]

# Configuration des sessions
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400  # Durée de vie de la session : 1 jour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Configuration des origines autorisées pour CORS (particulièrement pour les API)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",  # Pour le développement local
    "http://127.0.0.1:8000",  # Pour le développement local
]

# Configuration de Django REST Framework (pagination)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': 
        (
  'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Nombre d'éléments par page
}

# Configuration de Channels pour les WebSockets avec Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],  # Redis local
        },
    },
}


# Récupérer les valeurs des variables d'environnement
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

INTERNAL_IPS = ["127.0.0.1"]

# Recuécupérer les clés du CAPTCHA
# reCAPTCHA settings
USE_RECAPTCHA = not DEBUG  # Active le CAPTCHA seulement en production
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'