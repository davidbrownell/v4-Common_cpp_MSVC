# ----------------------------------------------------------------------
# |
# |  Setup_custom.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-09-23 09:30:57
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

import os
import sys
import uuid

from pathlib import Path
from typing import Dict, List, Optional, Union

from semantic_version import Version as SemVer          # pylint: disable=unused-import

from Common_Foundation.Shell.All import CurrentShell                        # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation.Shell import Commands                                # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation.Streams.DoneManager import DoneManager               # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation import Types                                         # type: ignore  # pylint: disable=import-error,unused-import

from RepositoryBootstrap import Configuration                               # type: ignore  # pylint: disable=import-error,unused-import
from RepositoryBootstrap import Constants                                   # type: ignore  # pylint: disable=import-error,unused-import


# ----------------------------------------------------------------------
from _install_data import MSVC_VERSIONS
del sys.modules["_install_data"]


# ----------------------------------------------------------------------
def GetConfigurations() -> Union[
    Configuration.Configuration,
    Dict[
        str,                                # configuration name
        Configuration.Configuration,
    ],
]:
    """Return configuration information for the repository"""

    if CurrentShell.family_name != "Windows":
        return {
            "noop": Configuration.Configuration(
                "MSVC tools are not supported on this operating system.",
                [
                    Configuration.Dependency(
                        uuid.UUID("DD6FCD30-B043-4058-B0D5-A6C8BC0374F4"),
                        "Common_Foundation",
                        "python310",
                        "https://github.com/davidbrownell/v4-Common_Foundation.git",
                    ),
                ],
                Configuration.VersionSpecs(
                    [],                             # tools
                    {},                             # libraries
                ),
            ),
        }

    configurations: Dict[str, Configuration.Configuration] = {}

    for version in MSVC_VERSIONS.keys():
        for architecture in ["x64", "x86"]:
            configurations["{}-{}".format(version, architecture)] = Configuration.Configuration(
                "MSVC tools '{}' targeting the '{}' architecture.".format(version, architecture),
                [
                    Configuration.Dependency(
                        uuid.UUID("d0ea9e4a-341b-409f-8bce-d1ea0efc202e"),
                        "Common_cpp_Development",
                        architecture,
                        "https://github.com/davidbrownell/v4-Common_cpp_Development.git",
                    ),
                ],
                Configuration.VersionSpecs(
                    [
                        Configuration.VersionInfo("MSVC", SemVer.coerce(version)),
                    ],
                    {},
                ),
            )

    return configurations


# ----------------------------------------------------------------------
# Note that it is safe to remove this function if it will never be used.
def GetCustomActions(
    # Note that it is safe to remove any parameters that are not used
    dm: DoneManager,
    explicit_configurations: Optional[List[str]],
    force: bool,
    interactive: Optional[bool],
) -> List[Commands.Command]:
    """Return custom actions invoked as part of the setup process for this repository"""

    commands: List[Commands.Command] = []

    root_dir = Path(__file__).parent
    assert root_dir.is_dir(), root_dir

    tools_dir = root_dir / Constants.TOOLS_SUBDIR
    assert tools_dir.is_dir(), tools_dir

    # Create a link to the foundation's .pylintrc file
    foundation_root_file = Path(Types.EnsureValid(os.getenv(Constants.DE_FOUNDATION_ROOT_NAME))) / ".pylintrc"
    assert foundation_root_file.is_file(), foundation_root_file

    commands.append(
        Commands.SymbolicLink(
            root_dir / foundation_root_file.name,
            foundation_root_file,
            remove_existing=True,
            relative_path=True,
        ),
    )

    with dm.Nested("\nProcessing 'Common_cpp_MSVC' tools...") as extract_dm:
        with extract_dm.Nested("Processing 'MSVC'...") as msvc_dm:
            for index, (version, install_data) in enumerate(MSVC_VERSIONS.items()):
                with msvc_dm.Nested(
                    "'{}' ({} of {})...".format(
                        version,
                        index + 1,
                        len(MSVC_VERSIONS),
                    ),
                ) as version_dm:
                    if explicit_configurations and not any(explicit_configuration.startswith(version) for explicit_configuration in explicit_configurations):
                        version_dm.WriteVerbose("The version was skipped.\n")
                        continue

                    install_data.installer.Install(
                        version_dm,
                        force=force,
                        prompt_for_interactive=install_data.prompt_for_interactive,
                        interactive=interactive,
                    )

    return commands
