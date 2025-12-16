@echo off
REM ============================================================
REM Database Setup Script for Windows
REM ============================================================
REM
REM This script initializes the database and creates an admin user
REM
REM Usage:
REM   setup_database.bat [config]
REM
REM Examples:
REM   setup_database.bat              (Development mode)
REM   setup_database.bat Production   (Production mode)
REM   setup_database.bat Testing      (Testing mode)
REM
REM ============================================================

echo.
echo ============================================================
echo   Dashboard Sonar - Database Setup
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
if not "%~1"=="" (
    set CONFIG=%~1
)

echo [+] Configuration: %CONFIG%
echo.

REM Run the setup script
python scripts\setup\setup_database.py --config %CONFIG%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   Setup completed successfully!
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   Setup failed with errors
    echo ============================================================
)

echo.
pause
