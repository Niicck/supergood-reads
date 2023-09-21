from .local import *

ALLOWED_HOSTS += ["testserver"]

# Remove postgres dependency for tests
INSTALLED_APPS = list(set(INSTALLED_APPS) - {"django.contrib.postgres"})
