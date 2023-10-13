from decouple import Csv, config

from .base import *

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="0.0.0.0,", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv())
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

STATIC_ROOT = PROJECT_ROOT / "staticfiles"
