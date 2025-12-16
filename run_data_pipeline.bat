@echo off
REM ============================================================================
REM Data Pipeline Orchestrator - Windows Wrapper
REM ============================================================================
REM
REM Executes all data processing scripts in the correct order.
REM Automatically loads environment variables from .env file.
REM
REM Usage:
REM     run_data_pipeline.bat [CONFIG] [EXTRA_ARGS...]
REM
REM Examples:
REM     run_data_pipeline.bat
REM     run_data_pipeline.bat Production
REM     run_data_pipeline.bat Development --clear-stats
REM     run_data_pipeline.bat Production --data-dir ./custom_datos
REM
REM Created: 2025-12-16
REM ============================================================================

setlocal enabledelayedexpansion

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo.
    echo [!] Error: Virtual environment is not activated
    echo [!] Please activate it first:
    echo [!]   venv\Scripts\activate
    echo.
    exit /b 1
)

echo ============================================================================
echo Data Pipeline Orchestrator
echo ============================================================================
echo.

REM Load environment variables from .env file
if exist .env (
    echo [+] Loading environment variables from .env file...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        REM Skip comments and empty lines
        echo %%a | findstr /r "^#" >nul
        if errorlevel 1 (
            if not "%%a"=="" (
                if not "%%b"=="" (
                    set "%%a=%%b"
                )
            )
        )
    )
    echo [+] Environment variables loaded successfully
    echo.
) else (
    echo [!] Warning: .env file not found
    echo [!] Database configuration must be set via environment variables
    echo.
)

REM Parse arguments
set CONFIG=%1
set EXTRA_ARGS=

REM Shift arguments if config is provided
if not "%CONFIG%"=="" (
    if /i "%CONFIG%"=="Development" (
        shift
    ) else if /i "%CONFIG%"=="Testing" (
        shift
    ) else if /i "%CONFIG%"=="Production" (
        shift
    ) else (
        REM First arg is not a config, treat as extra arg
        set CONFIG=
    )
)

REM Collect remaining arguments
:parse_args
if not "%1"=="" (
    set EXTRA_ARGS=!EXTRA_ARGS! %1
    shift
    goto parse_args
)

REM Build command
set CMD=python scripts\data\run_all_data_scripts.py

if not "%CONFIG%"=="" (
    set CMD=!CMD! --config %CONFIG%
)

if not "%EXTRA_ARGS%"=="" (
    set CMD=!CMD! %EXTRA_ARGS%
)

echo [*] Executing: !CMD!
echo.

REM Execute the script
!CMD!
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo [SUCCESS] Data pipeline completed successfully
) else (
    echo [FAILED] Data pipeline failed with exit code %EXIT_CODE%
)

exit /b %EXIT_CODE%
