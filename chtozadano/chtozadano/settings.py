import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

key = os.getenv("SECRET_KEY")
SECRET_KEY = key if key else "efndvnklrnekfnlax.zLKlwamdfkge"

DEBUG = str(os.getenv("DEBUG")).lower() == "true"

ALLOWED_HOSTS = str(os.getenv("ALLOWED_HOSTS")).split(",")

API_KEY = str(os.getenv("API_KEY"))

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "rest_framework",
    "homework.apps.HomeworkConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
    ],
}

ROOT_URLCONF = "chtozadano.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "INTERCEPT_REDIRECTS": False,
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
