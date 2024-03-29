import re
from pathlib import Path

import django_stubs_ext
from decouple import config

# Add type-checking for django
django_stubs_ext.monkeypatch()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


if config("DATABASE_URL", default=""):
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": config("DATABASE_ENGINE", default="django.db.backends.sqlite3"),
            "NAME": config("DATABASE_NAME", default=BASE_DIR / "db.sqlite3"),
            "USER": config("DATABASE_USER", default=""),
            "PASSWORD": config("DATABASE_PASSWORD", default=""),
            "HOST": config("DATABASE_HOST", default=""),
            "PORT": config("DATABASE_PORT", default=""),
            "TEST": {"NAME": config("DATABASE_NAME", default=":memory:")},
        },
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"

# When static assets are collected via "collectstatic" command, they will be loaded
# into this STATIC_ROOT directory.
# From there, they should be transfered to a proper file server.
# All other static file settings are handled in their respective Local or Production
# settings classes.
STATIC_ROOT = BASE_DIR / "staticfiles"

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Third Party
    "django_extensions",  # required by supergood_reads
    "django_vite",  # required by supergood_reads
    "widget_tweaks",  # required by supergood_reads
    "rest_framework",  # required by supergood_reads
    # Local
    "supergood_reads",  # add supergood_reads
    "demo",  # add your own local app
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
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# ---------------------
# Django Extensions
# ---------------------
SHELL_PLUS = "ipython"

# ---------------------
# Django-vite
# ---------------------
DJANGO_VITE_ASSETS_PATH = ""
DJANGO_VITE_DEV_MODE = config("DJANGO_VITE_DEV_MODE", default=False, cast=bool)
if not DJANGO_VITE_DEV_MODE:
    DJANGO_VITE_STATIC_URL_PREFIX = "supergood_reads/vite"
DJANGO_VITE_DEV_SERVER_PORT = config("DJANGO_VITE_DEV_SERVER_PORT", default="5173")
DJANGO_VITE_DEV_SERVER_HOST = config("DJANGO_VITE_DEV_SERVER_HOST", default="localhost")

STATICFILES_DIRS = [PROJECT_ROOT / "supergood_reads" / "vite_assets_dist"]

# ---------------------
# whitenoise
# ---------------------
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# http://whitenoise.evans.io/en/stable/django.html#WHITENOISE_IMMUTABLE_FILE_TEST
# https://github.com/MrBin99/django-vite/issues/30
def immutable_file_test(path, url):
    # Match filename with 8 or 12 hex digits before the extension.
    # Vite generates files with 8 hash digits.
    # Django generates files with 12 hash digits.
    # e.g. app.db8f2edc0c8a.js
    return re.match(r"^.+\.[0-9a-f]{8,12}\..+$", url)


WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test

# ---------------------
# supergood-reads
# ---------------------
SUPERGOOD_READS_CONFIG = "supergood_reads.utils.engine.DefaultSupergoodReadsConfig"
LOGIN_URL = config("LOGIN_URL", default="/auth/login/")
LOGIN_REDIRECT_URL = config("LOGIN_REDIRECT_URL", default="/reviews")
