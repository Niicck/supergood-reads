import re
import tempfile
from typing import Optional, Union


class PoetryInstallHelper:
    """
    Utility to help specify which poetry dependencies you wish to install in a nox
    session.

    Improvements over install_with_constraints:
        - supports exclusion of dependencies
        - supports spliting dev dependencies into multiple groups

    Arg:
        session: Session object from nox
    Kwargs:
        extra_groups: either a string or a list of strings of additional poetry
          dependency groups to install besides "main". "main" is always installed,
          but dependencies can be narrowed with allowlist or blocklist.
        allowlist: either a string or a list of strings of dependencies you want to
          constraint your install to use. Defaults to None.
        blocklist: either a string or a list of strings of dependencies you want to
          exclude from installation. Defaults to None.
        kwargs: additional kwargs you wish to pass to `session.install()`

    Examples:
        Install main dependencies only:
        PoetryInstallHelper(session).run()

        Install main with test dependencies, but exclude "django":
        PoetryInstallHelper(session, extra_groups="test", blocklist="django").run()

        Only install flake8:
        PoetryInstallHelper(session, extra_groups="lint", allowlist="flake8").run()

    Inspired by install_with_constraints:
    https://cjolowicz.github.io/posts/hypermodern-python-03-linting/#managing-dependencies-in-nox-sessions-with-poetry
    """

    # Regex to extract only direct dependencies from `poetry show --tree` output.
    POETRY_SHOW_DIRECT_DEPENDENCY_REGEX = "^\w\S*"

    def __init__(
        self,
        session,
        extra_groups: Optional[Union[str, list[str]]] = None,
        allowlist: Optional[Union[str, list[str]]] = None,
        blocklist: Optional[Union[str, list[str]]] = None,
        run: bool = True,
        **kwargs,
    ):
        self.session = session
        self.extra_groups = (
            [extra_groups] if isinstance(extra_groups, str) else extra_groups
        )
        self.allowlist = [allowlist] if isinstance(allowlist, str) else allowlist
        self.blocklist = [blocklist] if isinstance(blocklist, str) else blocklist
        self.kwargs = kwargs
        if run:
            self.run()

    def run(self):
        self.sanitize_allowlist()
        self.create_included_group_options()
        self.convert_blocklist_to_allowlist()
        self.install()

    def sanitize_allowlist(self):
        """
        Remove values in blocklist from allowlist.
        """
        if self.allowlist and self.blocklist:
            self.allowlist = list(set(self.allowlist) ^ set(self.blocklist))
            self.blocklist = None

    def create_included_group_options(self):
        """
        Convert list of groups into options consumable by `poetry install --only`
        """
        included_groups = {"main"}
        if self.extra_groups:
            included_groups = included_groups | set(self.extra_groups)

        included_group_options: list[str] = []
        for group in included_groups:
            included_group_options.append("--only")
            included_group_options.append(group)
        self.included_group_options = included_group_options

    def convert_blocklist_to_allowlist(self):
        """
        Pip does not allow users to exclude dependencies on install.

        To work around this, create a constraint allowlist that contains every
        dependency except for those that are part of the blacklist.
        """
        if self.blocklist:
            direct_dependencies = self.get_direct_dependencies()
            self.allowlist = list(set(direct_dependencies) ^ set(self.blocklist))

    def get_direct_dependencies(self):
        """
        Get list of all direct poetry dependencies for specified groups.
        """
        poetry_show_output = self.session.run(
            "poetry",
            "show",
            "--tree",
            *self.included_group_options,
            external=True,
            silent=True,
        )
        direct_dependencies = re.findall(
            self.POETRY_SHOW_DIRECT_DEPENDENCY_REGEX,
            poetry_show_output,
            re.M,
        )
        return direct_dependencies

    def install(self):
        """
        Export poetry dependencies and install using pip.
        Can constrain installed dependencies to those specified in allowlist.
        """
        with tempfile.NamedTemporaryFile() as requirements:
            self.session.run(
                "poetry",
                "export",
                *self.included_group_options,
                "--format=requirements.txt",
                f"--output={requirements.name}",
                # Workaround for bug with poetry and virtualenv interaction
                # https://github.com/cjolowicz/hypermodern-python/issues/174
                "--without-hashes",
                external=True,
            )
            if self.allowlist:
                self.session.install(
                    f"--constraint={requirements.name}", *self.allowlist, **self.kwargs
                )
            else:
                self.session.install("-r", requirements.name, **self.kwargs)
