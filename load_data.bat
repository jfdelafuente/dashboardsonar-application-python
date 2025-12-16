@echo off
REM ============================================================
REM Data Loading Script for Windows
REM ============================================================
REM
REM This script loads data from CSV files into the database
REM
REM Usage:
REM   load_data.bat [config] [options]
REM
REM Examples:
REM   load_data.bat                           (Development mode)
REM   load_data.bat Production                (Production mode)
REM   load_data.bat Development --batch-size 500
REM
REM ============================================================

echo.
echo ============================================================
echo   Dashboard Sonar - Data Loading
echo ============================================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo [!] Virtual environment not activated
    echo.
    echo Please activate your virtual environment first:
    echo   venv\Scripts\activate
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo [+] Virtual environment: %VIRTUAL_ENV%
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
    echo.
)

REM Determine configuration (default: Development)
set CONFIG=Development
set EXTRA_ARGS=

REM Parse arguments
:parse_args
if "%~1"=="" goto end_parse
if /i "%~1"=="Development" (
    set CONFIG=Development
    shift
    goto parse_args
)
if /i "%~1"=="Production" (
    set CONFIG=Production
    shift
    goto parse_args
)
if /i "%~1"=="Testing" (
    set CONFIG=Testing
    shift
    goto parse_args
)
REM Collect all other arguments as extra args
set EXTRA_ARGS=%EXTRA_ARGS% %~1
shift
goto parse_args
:end_parse

echo [+] Configuration: %CONFIG%
if not "%EXTRA_ARGS%"=="" (
    echo [+] Extra arguments:%EXTRA_ARGS%
)
echo.

REM Run the data loading script
python scripts\data\load_data.py --config %CONFIG%%EXTRA_ARGS%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   Data loading completed successfully!
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   Data loading failed with errors
    echo ============================================================
)

echo.
pause
