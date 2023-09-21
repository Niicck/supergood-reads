from decouple import config

from .base import *

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

DJANGO_VITE_ASSETS_PATH = (
    PROJECT_ROOT / "supergood_reads" / "static" / "supergood_reads" / "dist"
)
DJANGO_VITE_MANIFEST_PATH = DJANGO_VITE_ASSETS_PATH / "manifest.json"
DJANGO_VITE_DEV_MODE = config("DJANGO_VITE_DEV_MODE", default=False, cast=bool)
DJANGO_VITE_DEV_SERVER_PORT = config("DJANGO_VITE_DEV_SERVER_PORT")

STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH]
