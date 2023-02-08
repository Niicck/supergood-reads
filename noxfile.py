import nox

from tools.poetry_install_helper import PoetryInstallHelper

PYTHON_VERSIONS = [
    "3.8",
    "3.9",
    "3.10",
    "3.11",
]
DJANGO_VERSIONS = [
    "3.2",
    "4.0",
    "4.1",
]


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("django_version", DJANGO_VERSIONS)
def tests(session, django_version):
    args = session.posargs
    session.install(f"django=={django_version}")
    PoetryInstallHelper(session, extra_groups="test", blocklist="django")
    session.run("pytest", *args)
