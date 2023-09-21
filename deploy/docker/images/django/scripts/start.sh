#!/bin/bash

set -e

# navigate to project root directory
CURRENT_DIR=`dirname "${BASH_SOURCE[0]}"`
pushd "$CURRENT_DIR/../../../.." > /dev/null

# Apply migratiosn
python manage.py migrate

# Start server
if [ "$DJANGO_CONFIGURATION" == "Local" ]; then
    python \
        -Xfrozen_modules=off \
        -m debugpy --listen 0.0.0.0:${DEBUGPY_PORT} \
        manage.py runserver ${DJANGO_HOST}:${DJANGO_PORT} \
        --insecure
else
    echo "TODO"
    # gunicorn --workers=1 --bind=${DJANGO_HOST}:${DJANGO_PORT} --chdir=$ROOT_DIR cookiecutter_niicck_django.wsgi:application
fi
