# ----------------------------------------------------------------------
# |
# |  _install_data.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-10-17 11:02:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains data used during setup and activation"""

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, Optional

from Common_Foundation.Shell.All import CurrentShell                        # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation.Streams.DoneManager import DoneManager               # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation import SubprocessEx                                  # type: ignore  # pylint: disable=import-error,unused-import

from Common_Foundation import Types                                         # type: ignore  # pylint: disable=import-error,unused-import

from RepositoryBootstrap import Constants                                   # type: ignore  # pylint: disable=import-error,unused-import

from RepositoryBootstrap.SetupAndActivate.Installers.Installer import Installer                                     # type: ignore  # pylint: disable=import-error,unused-import


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InstallData(object):
    name: str
    installer: Installer
    prompt_for_interactive: bool            = field(kw_only=True)


# ----------------------------------------------------------------------
class _VisualStudioBuildToolsInstaller(Installer):
    # Release versions and URLs are available at https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history

    # ----------------------------------------------------------------------
    def __init__(
        self,
        version_dir: str,
        required_version: str,
        executable_name: str,
    ):
        super(_VisualStudioBuildToolsInstaller, self).__init__(
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
        dm: DoneManager,  # pylint: disable=unused-argument
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


# ----------------------------------------------------------------------
MSVC_VERSIONS: Dict[str, InstallData]       = {
    "17.4": InstallData(
        "MSVC",
        _VisualStudioBuildToolsInstaller(
            "v17.4",
            "17.4.p3",
            "vs_BuildTools_17.4.exe",
        ),
        prompt_for_interactive=True,
    ),
}
