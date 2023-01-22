SHELL := /bin/bash
-include .env

.PHONY: install
install:
	poetry

# Run pre-commit without commiting.
.PHONY: pre-commit
pre-commit:
	pre-commit

# Run mypy type checking.
# Not included in standard pre-commit because it takes a bit more time.
.PHONY: type-check
type-check:
	poetry run mypy django_flex_reviews

# Run your django app docker container
.PHONY: up
up:
	poetry run python manage.py runserver

# Start django python shell
.PHONY: shell
shell:
	poetry run python manage.py shell

# Start debugable python shell.
.PHONY: debug-shell
debug-shell:
	poetry run python -m debugpy --listen localhost:5678 manage.py shell

# Create a superuser for your django app
.PHONY: superuser
superuser:
	poetry run python manage.py createsuperuser

# Run pytest
.PHONY: pytest
pytest:
	poetry run pytest

# Run pytest with debugger
.PHONY: debug-pytest
debug-pytest:
	poetry run python -m debugpy --listen localhost:5678 --wait-for-client -m pytest
