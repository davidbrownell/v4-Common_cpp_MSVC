@echo off
@REM ----------------------------------------------------------------------
@REM |
@REM |  Uninstall.cmd
@REM |
@REM |  David Brownell <db@DavidBrownell.com>
@REM |      2022-09-23 10:19:24
@REM |
@REM ----------------------------------------------------------------------
@REM |
@REM |  Copyright David Brownell 2022
@REM |  Distributed under the Boost Software License, Version 1.0. See
@REM |  accompanying file LICENSE_1_0.txt or copy at
@REM |  http://www.boost.org/LICENSE_1_0.txt.
@REM |
@REM ----------------------------------------------------------------------

SET _MSVC_UNINSTALL_COMMAND_LINE_ARGS=^
    --force ^
    --installPath "%~dp0%DEVELOPMENT_ENVIRONMENT_ENVIRONMENT_NAME%" ^
    --nocache ^
    --wait

if "%1"=="--interactive" goto post_interactive

SET _MSVC_UNINSTALL_COMMAND_LINE_ARGS=%_MSVC_UNINSTALL_COMMAND_LINE_ARGS% --norestart --passive

:post_interactive

"%~dp0\vs_BuildTools_17.4.exe" uninstall %_MSVC_UNINSTALL_COMMAND_LINE_ARGS%
