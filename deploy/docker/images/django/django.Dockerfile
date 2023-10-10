# ---------------------
# Base
# ---------------------
FROM python:3.11-slim-bullseye as base

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

# ---------------------
# Local
# ---------------------
FROM base as local
ENV \
  DJANGO_SETTINGS_MODULE="demo.settings.local" \
  DJANGO_ENV="local"

# Install python requirements
COPY ./deploy/build/requirements/dev.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Copy application code to WORKDIR
COPY ./supergood_reads ./supergood_reads
COPY ./demo ./demo
COPY ./manage.py ./manage.py
COPY ./deploy/docker/images/django/scripts ./deploy/docker/images/django/scripts

ENTRYPOINT ./deploy/docker/images/django/scripts/entrypoint.sh $0 $@
CMD ./deploy/docker/images/django/scripts/start.sh

# ---------------------
# Deployed
# ---------------------
FROM base as deployed

# Install python requirements
COPY ./deploy/build/requirements/production.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Copy staticfiles
COPY deploy/build/collect_static staticfiles

# Copy application code to WORKDIR
COPY ./supergood_reads/ ./supergood_reads/
COPY ./demo/ ./demo/
COPY ./manage.py ./manage.py
COPY ./deploy/docker/images/django/scripts ./deploy/docker/images/django/scripts

ENTRYPOINT ./deploy/docker/images/django/scripts/entrypoint.sh $0 $@
CMD ./deploy/docker/images/django/scripts/start.sh

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
    DEBUG=false \
    DJANGO_SETTINGS_MODULE="demo.settings.production" \
    DJANGO_ENV="production"
