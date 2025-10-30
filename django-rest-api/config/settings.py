"""
Fichier de configuration principale du projet Django SoftDesk.
Gère les paramètres globaux de sécurité, base de données, REST Framework
et authentification OAuth2.
"""

import os
from pathlib import Path

import dj_database_url
from decouple import config

# ---------------------------------------------------------------------
# BASE DIR
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# CONFIGURATION DE BASE
# ---------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=lambda v: v.split(",")
)

# ---------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "oauth2_provider",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "api_auth",
    "users",
    "projects",
]

# ---------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ---------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------
# BASE DE DONNÉES
# ---------------------------------------------------------------------
# Par défaut : SQLite (en développement local)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Si DATABASE_URL est défini (GitHub Actions, production, etc.)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL, conn_max_age=600
    )

# ---------------------------------------------------------------------
# VALIDATION DES MOTS DE PASSE
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------------
# INTERNATIONALISATION
# ---------------------------------------------------------------------
LANGUAGE_CODE = "fr-FR"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# FICHIERS STATIQUES
# ---------------------------------------------------------------------
STATIC_URL = "static/"

# ---------------------------------------------------------------------
# UTILISATEURS ET AUTHENTIFICATION
# ---------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/api/projects/"
LOGOUT_REDIRECT_URL = "/api-auth/login/"

# ---------------------------------------------------------------------
# CONFIGURATION DES SESSIONS
# ---------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------
# REST FRAMEWORK
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "50/day",
        "invite": "5/minute",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DATETIME_FORMAT": "%d/%m/%Y %H:%M",
    "UNAUTHENTICATED_USER": None,
}

# ---------------------------------------------------------------------
# OAUTH2
# ---------------------------------------------------------------------
OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 36000,  # 10 heures
    "REFRESH_TOKEN_EXPIRE_SECONDS": 1209600,  # 14 jours
    "ROTATE_REFRESH_TOKEN": True,
    "SCOPES": {
        "read": "Lecture des données",
        "write": "Modification des données",
        "projects": "Accès aux projets SoftDesk",
    },
}

# ---------------------------------------------------------------------
# CACHE (OPTIMISATION LOCALE)
# ---------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",
        "TIMEOUT": 600,
    }
}

# ---------------------------------------------------------------------
# DOCUMENTATION
# ---------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "SoftDesk API",
    "DESCRIPTION": (
        "API REST sécurisée permettant la gestion de projets, issues "
        "et commentaires.\n\n"
        "Authentification via **OAuth2 (Bearer Token)**. "
        "Chaque requête vers une ressource protégée doit inclure :\n\n"
        "`Authorization: Bearer <access_token>`"
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "CONTACT": {"email": "support@softdesk.io"},
    "LICENSE": {"name": "MIT"},
    "SCHEMA_PATH_PREFIX": "/api",
    # --- Sécurité OAuth2 ---
    "SECURITY": [{"OAuth2": []}],
    "OAUTH2_FLOWS": {
        "password": {
            "tokenUrl": "/o/token/",
            "refreshUrl": "/o/token/",
            "scopes": {
                "read": "Lecture des données (GET).",
                "write": "Création et modification (POST, PUT, PATCH).",
                "delete": "Suppression des ressources (DELETE).",
            },
        },
    },
    # Force l’application du schéma OAuth2 sur toutes les vues
    "AUTHENTICATION_WHITELIST": [],  # désactive les overrides DRF
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/o/token/",
                        "refreshUrl": "/o/token/",
                        "scopes": {
                            "read": "Lecture des données",
                            "write": "Écriture / modification",
                            "delete": "Suppression",
                        },
                    }
                },
            }
        }
    },
    # --- Hook pour renommer le tag api-auth ---
    "POSTPROCESSING_HOOKS": [
        "utils.openapi_hooks.rename_auth_tag",
    ],
}


# ---------------------------------------------------------------------
# CONFIGURATION PAR DÉFAUT
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------
# LOGGING – Sécurité des invites / suppression de contributeurs
# ---------------------------------------------------------------------
LOG_DIR = Path(BASE_DIR) / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "[{asctime}] {levelname} " "[{name}:{lineno}] {message}"
            ),
            "style": "{",
        },
        "simple": {
            "format": "{levelname}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        # Fichier dédié aux logs des invitations
        "invites_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "invites.log"),
            "maxBytes": 2 * 1024 * 1024,  # 2 MB max
            "backupCount": 5,  # garde 5 fichiers de rotation
            "formatter": "verbose",
        },
        # Console (utile pour debug local)
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        # Logger pour les tentatives d’ajout / suppression
        "projects.invites": {
            "handlers": ["invites_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # Logger général Django
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
