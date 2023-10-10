#!/bin/bash

set -e

# navigate to project root directory
pushd "$APP_HOME" > /dev/null

# Apply migrations
python manage.py migrate

# Create groups and permissions
python manage.py supergood_reads_create_groups

# Create user_settings
python manage.py supergood_reads_create_user_settings

# Start server
if [ "$DJANGO_ENV" == "local" ]; then
    python \
        -Xfrozen_modules=off \
        -m debugpy --listen 0.0.0.0:${DEBUGPY_PORT} \
        manage.py runserver ${HOST}:${PORT} \
        --insecure
else
    gunicorn --workers=1 --bind=${HOST}:${PORT} --chdir=${APP_HOME} demo.wsgi:application
fi
