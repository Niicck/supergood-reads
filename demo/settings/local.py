from decouple import config

from .base import *

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

DJANGO_VITE_ASSETS_PATH = PROJECT_ROOT / "supergood_reads" / "assets" / "dist"
DJANGO_VITE_MANIFEST_PATH = DJANGO_VITE_ASSETS_PATH / "manifest.json"

STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH]
