#!/bin/bash
set -e -a

source .env

BUILD_TARGET="$1"

if [ -z "$BUILD_TARGET" ]; then
    echo "Please specify an environment: local, staging, or production."
    exit 1
fi

VERSION=$(python -c "from supergood_reads import __version__; print(__version__)")

if [ -z "$VERSION" ]; then
    echo "supergood_reads/__init__.py does not specify a __version__."
    exit 1
fi

# This is the image tag for the django app. It is consumed by the "app" service in docker-compose.yml
DOCKER_APP_IMAGE_REPO="${COMPOSE_PROJECT_NAME}-${BUILD_TARGET}"
DOCKER_APP_IMAGE_TAG="v${VERSION}"
DOCKER_APP_IMAGE_TAG_LATEST="latest"

DOCKER_COMPOSE_DIR="./deploy/docker/compose"
CURRENT_DIR=`dirname "${BASH_SOURCE[0]}"`
PROJECT_ROOT_DIR="$CURRENT_DIR/../.."

# Navigate to project root directory
pushd "$PROJECT_ROOT_DIR" > /dev/null

case $BUILD_TARGET in
    local)
        make dev-requirements
        docker compose \
            -f ${DOCKER_COMPOSE_DIR}/docker-compose.yml \
            -f ${DOCKER_COMPOSE_DIR}/docker-compose.local.yml \
            --env-file .env \
            build
        ;;
    staging)
        echo "TODO"
        exit 1
        ;;
    production)
        make production-requirements
        make build-vite
        make collectstatic
        docker build \
            -f ./deploy/docker/images/django/django.Dockerfile \
            -t $DOCKER_APP_IMAGE_REPO:$DOCKER_APP_IMAGE_TAG \
            --target $BUILD_TARGET \
            --progress=plain \
            .
        ;;
    *)
        echo "Invalid environment specified. Use local, staging, or production."
        exit 1
        ;;
esac

# Add "latest" tag to created image
docker tag $DOCKER_APP_IMAGE_REPO:$DOCKER_APP_IMAGE_TAG $DOCKER_APP_IMAGE_REPO:$DOCKER_APP_IMAGE_TAG_LATEST

# Tag for Docker Hub
docker tag $DOCKER_APP_IMAGE_REPO:$DOCKER_APP_IMAGE_TAG $DOCKER_HUB_REPO:$DOCKER_APP_IMAGE_TAG_LATEST
