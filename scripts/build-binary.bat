@echo off
REM Build OpenJarvis standalone binary for Windows

setlocal enabledelayedexpansion

set OUTPUT_DIR=dist

:parse_args
if "%~1"=="" goto check_toolchain
if "%~1"=="--output-dir" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto parse_args
)
echo Unknown option: %~1
echo Usage: %0 [--output-dir DIR]
exit /b 1

:check_toolchain
echo Checking build toolchain...
where gcc >nul 2>&1
if %errorlevel% neq 0 (
    where cl >nul 2>&1
    if !errorlevel! neq 0 (
        echo Error: No C compiler found.
        echo Install Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        exit /b 1
    )
)

echo Installing build dependencies...
uv sync --group build

echo Building binary...
uv run python build\build.py --output-dir %OUTPUT_DIR%

echo Build complete!
