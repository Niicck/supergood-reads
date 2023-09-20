"""
Django settings for sample_app project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

import django_stubs_ext
import environ

# Add type-checking for django
django_stubs_ext.monkeypatch()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

# Read .env file
env = environ.Env()
environ.Env.read_env(os.path.join(PROJECT_ROOT, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ROOT_URLCONF = "tests.sample_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_ROOT / "supergood_reads" / "static"
MEDIA_URL = "/media/"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": env("DATABASE_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        "USER": env("DATABASE_USER", default=""),
        "PASSWORD": env("DATABASE_PASSWORD", default=""),
        "HOST": env("DATABASE_HOST", default=""),
        "PORT": env("DATABASE_PORT", default=""),
        "TEST": {"NAME": env("DATABASE_NAME", default=":memory:")},
    },
}

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local
    "supergood_reads",  # add supergood_reads
    "tests.sample_app",  # add your own local app
    # Third Party
    "django_extensions",
    "django_vite",  # add django-vite
    "widget_tweaks",  # add django-widget-tweaks
    "rest_framework",  # add rest-framework
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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

# django-extensions
SHELL_PLUS = "ipython"

# django-vite
DJANGO_VITE_ASSETS_PATH = (
    PROJECT_ROOT / "supergood_reads" / "static" / "supergood_reads" / "dist"
)
DJANGO_VITE_MANIFEST_PATH = (
    PROJECT_ROOT
    / "supergood_reads"
    / "static"
    / "supergood_reads"
    / "dist"
    / "manifest.json"
)
DJANGO_VITE_DEV_MODE = True
DJANGO_VITE_DEV_SERVER_PORT = env("DJANGO_VITE_DEV_SERVER_PORT")
STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH]

# supergood-reads
SUPERGOOD_READS_CONFIG = "supergood_reads.utils.engine.DefaultSupergoodReadsConfig"
LOGIN_URL = "/reads-app/auth/login/"
LOGIN_REDIRECT_URL = "/reads-app/reviews"
