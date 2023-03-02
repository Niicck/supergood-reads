import tempfile
from pathlib import Path

import nox

PYTHON_VERSIONS = ["3.11", "3.10", "3.9", "3.8"]
DJANGO_VERSIONS = ["4.1", "4.0", "3.2"]


def install_poetry_groups(session, *groups: str) -> None:
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
def lint(session: nox.Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
    ]
    session.run("pre-commit", *args, external=True)


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("django_version", DJANGO_VERSIONS)
def test(session: nox.Session, django_version: str) -> None:
    """Run the pytest suite."""
    args = session.posargs
    install_poetry_groups(session, "main", "test", "dev", "coverage")
    session.install(f"django=={django_version}")
    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *args)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=PYTHON_VERSIONS)
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["django_flex_reviews", "tests"]
    install_poetry_groups(session, "main", "dev", "test", "mypy")
    session.run("mypy", *args)


@nox.session(python=PYTHON_VERSIONS[0])
def safety(session: nox.Session) -> None:
    """Scan dependencies for insecure packages."""
    install_poetry_groups(session, "safety")
    session.run(
        "bash",
        "-c",
        "poetry export --format=requirements.txt | safety check --full-report --stdin",
        external=True,
    )


@nox.session(python=PYTHON_VERSIONS[0])
def coverage(session: nox.Session) -> None:
    """Produce the coverage report.

    Combines the results from all test runs from all versions of python. This is because
    some logic branches may only apply to certain versions of python - we want to avoid
    false negative coverage failures when those branches aren't covered by pytest runs
    from other python versions.
    """
    args = session.posargs or ["report"]
    install_poetry_groups(session, "coverage")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)
