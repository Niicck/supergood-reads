from decouple import Csv, config

from .base import *

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="0.0.0.0,", cast=Csv())

STATIC_ROOT = PROJECT_ROOT / "staticfiles"
