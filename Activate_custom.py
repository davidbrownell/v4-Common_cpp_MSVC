# ----------------------------------------------------------------------
# |
# |  Activate_custom.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-09-23 11:11:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
# pylint: disable=missing-module-docstring

import sys

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional

from semantic_version import Version as SemVer

from Common_Foundation.Shell import Commands                                # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation.Shell.All import CurrentShell                        # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation.Streams.DoneManager import DoneManager               # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation import SubprocessEx                                  # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation import Types                                         # type: ignore  # pylint: disable=import-error,unused-import

from RepositoryBootstrap import Configuration                                       # type: ignore  # pylint: disable=import-error,unused-import
from RepositoryBootstrap import Constants                                           # type: ignore  # pylint: disable=import-error,unused-import
from RepositoryBootstrap import DataTypes                                           # type: ignore  # pylint: disable=import-error,unused-import
from RepositoryBootstrap.ActivateActivity import ActivateActivity           # type: ignore  # pylint: disable=import-error,unused-import
from RepositoryBootstrap.SetupAndActivate.Installers.Installer import Installer     # type: ignore  # pylint: disable=import-error,unused-import


# ----------------------------------------------------------------------
from _install_data import MSVC_VERSIONS
del sys.modules["_install_data"]


# ----------------------------------------------------------------------
# Note that it is safe to remove this function if it will never be used.
def GetCustomActions(                                                       # pylint: disable=too-many-arguments
    # Note that it is safe to remove any parameters that are not used
    dm: DoneManager,                                                        # pylint: disable=unused-argument
    repositories: List[DataTypes.ConfiguredRepoDataWithPath],               # pylint: disable=unused-argument
    generated_dir: Path,                                                    # pylint: disable=unused-argument
    configuration: Optional[str],                                           # pylint: disable=unused-argument
    version_specs: Configuration.VersionSpecs,                              # pylint: disable=unused-argument
    force: bool,                                                            # pylint: disable=unused-argument
    is_mixin_repo: bool,                                                    # pylint: disable=unused-argument
) -> List[Commands.Command]:
    assert configuration is not None
    if configuration == "noop":
        return []

    commands: List[Commands.Command] = []

    this_dir = Path(__file__).parent
    assert this_dir.is_dir(), this_dir

    tools_dir = this_dir / Constants.TOOLS_SUBDIR
    assert tools_dir.is_dir(), tools_dir

    assert configuration is not None
    msvc_version, architecture = configuration.split("-")

    # Validate the dynamically installed content
    with dm.Nested("Validating 'MSVC'...") as msvc_dm:
        install_data = MSVC_VERSIONS.get(msvc_version, None)
        assert install_data is not None, msvc_version

        installer = install_data.installer

        installer.ShouldInstall(None, lambda reason: msvc_dm.WriteError(reason))

    # Initialize Visual Studio Build Tools
    if architecture == "x64":
        activate_name = "vcvars64.bat"
    elif architecture == "x86":
        activate_name = "vcvarsamd64_x86.bat"
    else:
        assert False, architecture  # pragma: no cover

    activate_path = installer.output_dir / "VC" / "Auxiliary" / "Build" / activate_name
    assert activate_path.is_file(), activate_path

    commands += [
        Commands.Raw('call "{}"'.format(activate_path)),
        Commands.Set("DEVELOPMENT_ENVIRONMENT_CPP_COMPILER_NAME", "MSVC"),
    ]

    return commands


# ----------------------------------------------------------------------
# Note that it is safe to remove this function if it will never be used.
def GetCustomActionsEpilogue(                                               # pylint: disable=too-many-arguments
    # Note that it is safe to remove any parameters that are not used
    dm: DoneManager,                                                        # pylint: disable=unused-argument
    repositories: List[DataTypes.ConfiguredRepoDataWithPath],               # pylint: disable=unused-argument
    generated_dir: Path,                                                    # pylint: disable=unused-argument
    configuration: Optional[str],                                           # pylint: disable=unused-argument
    version_specs: Configuration.VersionSpecs,                              # pylint: disable=unused-argument
    force: bool,                                                            # pylint: disable=unused-argument
    is_mixin_repo: bool,                                                    # pylint: disable=unused-argument
) -> List[Commands.Command]:
    """\
    Returns a list of actions that should be invoked as part of the activation process. Note
    that this is called after `GetCustomActions` has been called for each repository in the dependency
    list.

    ********************************************************************************************
    Note that it is very rare to have the need to implement this method. In most cases, it is
    safe to delete the entire method. However, keeping the default implementation (that
    essentially does nothing) is not a problem.
    ********************************************************************************************
    """

    return []


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Installer(Installer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        version_dir: str,
        required_version: str,
        executable_name: str,
    ):
        super(_Installer, self).__init__(
            Path(__file__).parent / Constants.TOOLS_SUBDIR / "MSVC" / version_dir / CurrentShell.family_name / "x64",
            required_version,
            sentinel_lives_in_tool_root=True,
        )

        self.executable_name                = executable_name

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Types.overridemethod
    @contextmanager
    def _YieldInstallSource(
        self,
        dm: DoneManager,
    ) -> Iterator[Optional[Path]]:
        yield self.tool_dir / self.executable_name

    # ----------------------------------------------------------------------
    @Types.overridemethod
    def _Install(
        self,
        dm: DoneManager,
        install_source: Path,  # pylint: disable=unused-argument
        *,
        is_interactive: bool=False,
    ) -> None:
        self.__class__._Execute(  # pylint: disable=protected-access
            dm,
            '"{}"{}'.format(
                self.tool_dir / "Setup.cmd",
                " --interactive" if is_interactive else "",
            ),
        )

    # ----------------------------------------------------------------------
    @Types.overridemethod
    def _Uninstall(
        self,
        dm: DoneManager,
        *,
        is_interactive: bool=False,
    ) -> None:
        self.__class__._Execute(
            dm,
            '"{}"{}'.format(  # pylint: disable=protected-access
                self.tool_dir / "Uninstall.cmd",
                " --interactive" if is_interactive else "",
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def _Execute(
        dm: DoneManager,
        command_line: str,
    ) -> None:
        result = SubprocessEx.Run(command_line)

        dm.result = result.returncode

        if dm.result != 0:
            dm.WriteError(result.output)
            return

        with dm.YieldVerboseStream() as stream:
            stream.write(result.output)
