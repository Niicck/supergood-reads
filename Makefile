SHELL := /bin/bash
-include .env

VERSION := $(shell python -c "from supergood_reads import __version__; print(__version__)")

# ---------------------
# Setup
# ---------------------

# Create .env from template if .env doesn't already exist
.env:
	cp -n ./tools/.env-sample .env

# Install pre-commit
.PHONY: install-pre-commit
install-pre-commit:
	pre-commit install

.PHONY: install-nox
install-nox:
	pip install --upgrade nox

.PHONY: setup
setup: .env install-pre-commit install-nox

# ---------------------
# QA
# ---------------------

# Lint all files using pre-commit
.PHONY: lint
lint:
	nox -rs lint

# Scan dependencies for insecure packages
.PHONY: safety
safety:
	nox -rs safety

# Run mypy type checking for python files.
.PHONY: mypy
mypy:
	nox -rs mypy-3.11

# Run typescript type checking for typescript files.
.PHONY: tsc-check
tsc-check:
	npx tsc --noEmit --incremental

# Run pytest via nox. Includes coverage check
.PHONY: pytest
pytest:
	nox -rs "test-3.11(django_version='4.2')"

# Run pytest with debugger
.PHONY: debug-pytest
debug-pytest:
	poetry run python -m debugpy --listen localhost:${DEBUGPY_PORT_PYTEST} --wait-for-client -m pytest

# Run frontend javascript tests with jest.
.PHONY: jest
jest:
	npm run jest

# ---------------------
# Run on Local Machine
# ---------------------

# Install poetry dependencies
.PHONY: install
install:
	poetry install --with dev,app

# Run django app
.PHONY: up
up:
	poetry run python manage.py runserver ${DJANGO_PORT}

# Run vite static asset compilation dev server
.PHONY: vite
vite:
	npm run dev

# Run django app with debugger enabled
.PHONY: debug-up
debug-up:
	poetry run python -m debugpy --listen localhost:${DEBUGPY_PORT} manage.py runserver ${DJANGO_PORT}

# Start django python shell
.PHONY: shell
shell:
	poetry run python manage.py shell_plus

# Start debugable python shell.
.PHONY: debug-shell
debug-shell:
	poetry run python -m debugpy --listen localhost:${DEBUGPY_PORT} manage.py shell_plus

# Create a superuser for your django app
.PHONY: superuser
superuser:
	poetry run python manage.py createsuperuser

# Start poetry venv
.PHONY: venv
venv:
	source "$(poetry env info --path)/bin/activate"

# ---------------------
# Run on Docker
# ---------------------

DOCKER_COMPOSE_DIR := ./deploy/docker/compose

# Run your django app docker container
.PHONY: docker-up
docker-up:
	docker compose \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.yml \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.local.yml \
		--env-file .env \
		up

# Kill and restart your django app docker container
.PHONY: docker-restart
docker-restart:
	docker compose \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.yml \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.local.yml \
		--env-file .env \
		kill app
	docker compose \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.yml \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.local.yml \
		--env-file .env \
		restart app

# Run a django app docker container without runserver
.PHONY: docker-troubleshoot
docker-troubleshoot:
	docker compose \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.yml \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.local.yml \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.troubleshooting.yml \
		--env-file .env \
		up

# Enter into the postgres db shell inside your running postgres container
.PHONY: db-shell
db-shell:
	docker exec -it ${COMPOSE_PROJECT_NAME}-db-1 psql -U ${POSTGRES_USER} -p ${POSTGRES_PORT}  -d ${POSTGRES_DB} -w

# Enter into a bash shell inside your running django app docker container
.PHONY: docker-shell
docker-shell:
	docker exec -it ${COMPOSE_PROJECT_NAME}-app-1 /bin/bash

# Enter into the django python shell inside your running django app docker container
.PHONY: docker-shell-plus
docker-shell-plus:
	docker exec -it ${COMPOSE_PROJECT_NAME}-app-1 python manage.py shell_plus

# ---------------------
# Build
# ---------------------

# collect static django assets
.PHONY: collectstatic
collectstatic:
	poetry run python manage.py collectstatic

# compile vite assets for production
.PHONY: build-vite
build-vite:
	npm run build

# Build "deploy/build/requirements/dev.txt"
.PHONY: dev-requirements
dev-requirements:
	python ./deploy/scripts/build_requirements.py --dev

# Build "deploy/build/requirements/production.txt"
.PHONY: production-requirements
production-requirements:
	python ./deploy/scripts/build_requirements.py

# Build local django app docker container
.PHONY: build-local
build-local:
	sh ./deploy/scripts/build_container.sh local

# Build local django app docker container
build-production: production-requirements collectstatic
	docker compose \
		-f ${DOCKER_COMPOSE_DIR}/docker-compose.yml \
		--env-file .env \
		build
