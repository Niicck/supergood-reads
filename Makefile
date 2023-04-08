SHELL := /bin/bash
-include .env

.PHONY: install
install:
	poetry install --with dev

# Start venv
.PHONY: venv
venv:
	source "$(poetry env info --path)/bin/activate"

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

# Create .env from template if .env doesn't already exist
.env:
	cp -n ./tools/.env-sample .env

# Run django app
.PHONY: up
up:
	poetry run python manage.py runserver ${DJANGO_RUNSERVER_PORT}

# Run django app with debugger enabled
.PHONY: debug-up
debug-up:
	poetry run python -m debugpy --listen localhost:5678 manage.py runserver ${DJANGO_RUNSERVER_PORT}

# Run vite static asset compilation
.PHONY: vite
vite:
	npm run dev

# Start django python shell
.PHONY: shell
shell:
	poetry run python manage.py shell_plus

# Start debugable python shell.
.PHONY: debug-shell
debug-shell:
	poetry run python -m debugpy --listen localhost:5678 manage.py shell_plus

# Create a superuser for your django app
.PHONY: superuser
superuser:
	poetry run python manage.py createsuperuser

# Run pytest via nox. Includes coverage check
.PHONY: pytest
pytest:
	nox -rs "test-3.11(django_version='4.1')"

# Run pytest with debugger
.PHONY: debug-pytest
debug-pytest:
	poetry run python -m debugpy --listen localhost:5678 --wait-for-client -m pytest

# Run frontend javascript tests with jest.
.PHONY: jest
jest:
	npm run jest
