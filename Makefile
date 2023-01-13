SHELL := /bin/bash
-include .env

.PHONY: install pre-commit type-check env-file build up shell shell_plus db_shell superuser

install:
	poetry

# Run pre-commit without commiting.
pre-commit:
	pre-commit

# Run mypy type checking.
# Not included in standard pre-commit because it takes a bit more time.
type-check:
	poetry run mypy cookiecutter_niicck_django

# Create .env from template if .env doesn't already exist
env-file:
	cp -n ./utils/.env-sample .env

# Build your django app docker container
build:
	sh ./utils/build_requirements_txt.sh
	docker compose \
		-f ./docker/docker-compose.yml \
		-f ./docker/docker-compose.local.yml \
		--env-file .env \
		build

# Run your django app docker container
up:
	docker compose \
		-f ./docker/docker-compose.yml \
		-f ./docker/docker-compose.local.yml \
		--env-file .env \
		up

# Run a django app docker container without runserver
troubleshoot:
	docker compose \
		-f ./docker/docker-compose.yml \
		-f ./docker/docker-compose.local.yml \
		-f ./docker/docker-compose.troubleshooting.yml \
		--env-file .env \
		up

# Enter into a bash shell inside your running django app docker container
shell:
	docker exec -it docker-app-1 /bin/bash

# Enter into the django python shell inside your running django app docker container
shell_plus:
	docker exec -it docker-app-1 python manage.py shell_plus

# Enter into the postgres db shell inside your running postgres container
db-shell:
	docker exec -it docker-db-1 psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -w

# Create a superuser for your django app
superuser:
	docker exec -it docker-app-1 python manage.py createsuperuser
