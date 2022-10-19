@echo off
@REM ----------------------------------------------------------------------
@REM |
@REM |  Setup.cmd
@REM |
@REM |  David Brownell <db@DavidBrownell.com>
@REM |      2022-09-23 09:55:39
@REM |
@REM ----------------------------------------------------------------------
@REM |
@REM |  Copyright David Brownell 2022
@REM |  Distributed under the Boost Software License, Version 1.0. See
@REM |  accompanying file LICENSE_1_0.txt or copy at
@REM |  http://www.boost.org/LICENSE_1_0.txt.
@REM |
@REM ----------------------------------------------------------------------

SET _MSVC_SETUP_COMMAND_LINE_ARGS=^
    --force ^
    --installPath "%~dp0%DEVELOPMENT_ENVIRONMENT_ENVIRONMENT_NAME%" ^
    --nickname "17.4-Local" ^
    --nocache ^
    --wait ^
    --add "Microsoft.VisualStudio.Component.Roslyn.Compiler" ^
    --add "Microsoft.Component.MSBuild" ^
    --add "Microsoft.VisualStudio.Component.CoreBuildTools" ^
    --add "Microsoft.VisualStudio.Workload.MSBuildTools" ^
    --add "Microsoft.VisualStudio.Component.Windows10SDK" ^
    --add "Microsoft.VisualStudio.Component.VC.CoreBuildTools" ^
    --add "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" ^
    --add "Microsoft.VisualStudio.Component.VC.Redist.14.Latest" ^
    --add "Microsoft.VisualStudio.Component.VC.ASAN" ^
    --add "Microsoft.VisualStudio.Component.TextTemplating" ^
    --add "Microsoft.VisualStudio.Component.VC.CoreIde" ^
    --add "Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core" ^
    --add "Microsoft.VisualStudio.Component.Windows11SDK.22621" ^
    --add "Microsoft.VisualStudio.Workload.VCTools"

if "%1"=="--interactive" goto post_interactive

SET _MSVC_SETUP_COMMAND_LINE_ARGS=%_MSVC_SETUP_COMMAND_LINE_ARGS% --norestart --passive

:post_interactive

"%~dp0\vs_BuildTools_17.4.exe" %_MSVC_SETUP_COMMAND_LINE_ARGS%
