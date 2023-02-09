"""Nox sessions."""
import tempfile

import nox

PYTHON_VERSIONS = ["3.11", "3.10", "3.9", "3.8"]
DJANGO_VERSIONS = ["4.1", "4.0", "3.2"]


def install_poetry_groups(session, *groups: str):
    """Install dependencies from poetry groups.

    Using this as s workaround until my PR is merged in:
    https://github.com/cjolowicz/nox-poetry/pull/1080
    """
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            *[f"--only={group}" for group in groups],
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("-r", requirements.name)


@nox.session(python=PYTHON_VERSIONS[0])
def lint(session):
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
    ]
    session.run("pre-commit", *args, external=True)


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("django_version", DJANGO_VERSIONS)
def test(session, django_version):
    """Run the pytest suite."""
    args = session.posargs
    install_poetry_groups(session, "main", "test")
    session.install(f"django=={django_version}")
    session.run("pytest", *args)


@nox.session(python=PYTHON_VERSIONS)
def mypy(session):
    """Type-check using mypy."""
    args = session.posargs or ["django_flex_reviews", "tests"]
    install_poetry_groups(session, "mypy")
    session.run("mypy", *args)
    session.run("mypy", "noxfile.py")


@nox.session(python=PYTHON_VERSIONS[0])
def safety(session) -> None:
    """Scan dependencies for insecure packages."""
    install_poetry_groups(session, "safety")
    session.run(
        "bash",
        "-c",
        "poetry export --format=requirements.txt | safety check --full-report --stdin",
        external=True,
    )
