###
# base image
###
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
WORKDIR ${APP_HOME}

# Python ENV vars
ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# App ENV vars
ENV \
    DJANGO_PORT \
    DJANGO_HOST \
    POSTGRES_DB \
    POSTGRES_USER \
    POSTGRES_PASSWORD \
    POSTGRES_HOST \
    POSTGRES_PORT \
    DEBUG \
    SECRET_KEY \
    DJANGO_CONFIGURATION

# Install python packages
COPY ./build/requirements/dev.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy application code to WORKDIR
COPY . ${APP_HOME}

ENTRYPOINT ./docker/images/django/scripts/entrypoint.sh $0 $@
CMD ./docker/images/django/scripts/start.sh

###
# local image
###
FROM base as local

ENV \
    DEBUGPY_PORT=

###
# deployed image
###
FROM base as deployed
