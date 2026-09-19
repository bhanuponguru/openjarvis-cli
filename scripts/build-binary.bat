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
echo Installing build dependencies...
uv sync --group build

echo Building binary...
uv run python build\build.py --output-dir %OUTPUT_DIR%

echo Build complete!
