from .base import *

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# Automatically adds --nostatic flag to runserver so that whitenoise is used
# instead of runserver's default staticfile handling.
INSTALLED_APPS += ["whitenoise.runserver_nostatic"]
