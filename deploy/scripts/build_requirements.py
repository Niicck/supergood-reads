"""
Exports poetry project.toml dependencies to a requirements.txt file.
That requirements.txt file will then be used to install python dependencies within
the django docker container.

To build "deploy/build/requirements/production.txt":
    python build_requirements.py

To build "deply/build/requirements/dev.txt":
    python build_requirements.py --dev
"""

import argparse
import subprocess  # noqa: S404
from pathlib import Path


def get_is_dev():
    """
    Check if we passed a --dev flag to file invocation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()
    is_dev = args.dev
    return is_dev


class BuildRequirementsHandler:
    """
    Exports poetry project.toml dependencies to a requirements.txt file.
    That requirements.txt file will then be used to install python dependencies within
    your django docker container.

    Exported file will end up in the "build/requirements/" directory.
    If is_dev=True, then it will create a dev.txt file containing dev dependencies.
    If is_dev=False (default), then it will create a production.txt file which excludes
    dev dependencies.

    Args:
        is_dev: Flag to indicate if we want to create a export containing dev
            dependencies.
    """

    def __init__(self, is_dev=False):
        self.is_dev = is_dev

    def run(self):
        self.set_file_dest()
        self.export()

    def set_file_dest(self):
        requirements_dir = (
            Path(__file__).resolve().parent.parent / "build" / "requirements"
        )
        file_name = "dev.txt" if self.is_dev else "production.txt"
        self.file_dest = requirements_dir / file_name

    def export(self):
        export_cmd = (
            f"poetry export -f requirements.txt -o '{self.file_dest}' --with app"
        )
        if self.is_dev:
            export_cmd = export_cmd + " --with dev"
        process = subprocess.run(
            export_cmd, stderr=subprocess.STDOUT, shell=True  # noqa: S602
        )
        process.check_returncode()


if __name__ == "__main__":
    is_dev = get_is_dev()
    handler = BuildRequirementsHandler(is_dev=is_dev)
    handler.run()
