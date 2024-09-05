import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = str(os.getenv("DEBUG", "False")).lower() == "true"

ALLOWED_HOSTS = str(os.getenv("ALLOWED_HOSTS")).split(",")

CSRF_TRUSTED_ORIGINS = str(
    os.getenv("CSRF_TRUSTED_ORIGINS", ["http://bot:8000", "http://localhost"]),
).split(",")

SITE_TECHNICAL_WORKS = (
    str(os.getenv("SITE_TECHNICAL_WORKS", "False")).lower() == "true"
)
API_TECHNICAL_WORKS = (
    str(os.getenv("API_TECHNICAL_WORKS", "False")).lower() == "true"
)

DEBUG_PROPAGATE_EXCEPTIONS = (
    str(os.getenv("DEBUG_PROPAGATE_EXCEPTIONS", "False")).lower() == "true"
)

API_KEY = str(os.getenv("API_KEY"))

INTERNAL_IPS = str(os.getenv("INTERNAL_IPS", "127.0.0.1")).split(",")

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cleanup.apps.CleanupConfig",
    "rest_framework",
    "colorfield",
    "homework.apps.HomeworkConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "chtozadano.middleware.APIKeyMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

if DEBUG:
    render_class_now = REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]
    render_class_now.append("rest_framework.renderers.BrowsableAPIRenderer")
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = render_class_now


ROOT_URLCONF = "chtozadano.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "chtozadano.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": str(os.getenv("POSTGRES_NAME")),
        "USER": str(os.getenv("POSTGRES_USER")),
        "PASSWORD": str(os.getenv("POSTGRES_PASSWORD")),
        "HOST": str(os.getenv("POSTGRES_HOST")),
        "PORT": str(os.getenv("POSTGRES_PORT")),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth."
        "password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth"
        ".password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth"
        ".password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth"
        ".password_validation.NumericPasswordValidator",
    },
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
        "INTERCEPT_REDIRECTS": False,
        "IS_RUNNING_TESTS": False,
    }

if API_TECHNICAL_WORKS:
    MIDDLEWARE.append("chtozadano.middleware.APITechnicalWorksMiddleware")


if SITE_TECHNICAL_WORKS:
    MIDDLEWARE.append("chtozadano.middleware.SiteTechnicalWorksMiddleware")

if str(os.getenv("USE_REDIS", "True").lower()) == "true":
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis:6379/0",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        },
    }

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = False

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
