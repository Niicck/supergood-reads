# ---------------------
# Base
# ---------------------
FROM python:3.11-slim-bullseye as base

# Build argument to parameterize the requirements file
ARG REQUIREMENTS_FILE

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    # For building Python packages
    build-essential \
    # psycopg2 dependencies
    libpq-dev \
    # For troubleshooting
    curl

# Set working directory
ARG APP_HOME=/app
ENV APP_HOME ${APP_HOME}
WORKDIR ${APP_HOME}

# Python ENV vars
ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install python requirements
COPY ./deploy/build/requirements/${REQUIREMENTS_FILE} ./requirements.txt
RUN pip install -r ./requirements.txt

# Copy application code to WORKDIR
COPY ./supergood_reads ./supergood_reads
COPY ./demo ./demo
COPY ./manage.py ./manage.py
COPY ./deploy/docker/images/django/scripts ./deploy/docker/images/django/scripts

ENTRYPOINT ./deploy/docker/images/django/scripts/entrypoint.sh $0 $@
CMD ./deploy/docker/images/django/scripts/start.sh

# ---------------------
# Local
# ---------------------
FROM base as local
ENV \
  DJANGO_SETTINGS_MODULE="demo.settings.local" \
  DJANGO_ENV="local"

# ---------------------
# Deployed
# ---------------------
FROM base as deployed

ENV \
    DEBUG=false

# ---------------------
# Staging
# ---------------------
FROM deployed as staging

ENV \
  DJANGO_SETTINGS_MODULE="demo.settings.staging" \
  DJANGO_ENV="staging"

# ---------------------
# Production
# ---------------------
FROM deployed as production

ENV \
    DJANGO_SETTINGS_MODULE="demo.settings.production" \
    DJANGO_ENV="production"
