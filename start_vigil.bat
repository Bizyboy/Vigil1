@echo off
title Vigil - The Watchful Guardian
echo.
echo ═══════════════════════════════════════════════════════════════
echo                    VIGIL - THE WATCHFUL GUARDIAN
echo ══════════════════════════���════════════════════════════════════
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: Check if .env exists
if not exist "config\.env" (
    echo.
    echo WARNING: config\.env file not found!
    echo Please copy config\.env.example to config\.env
    echo and fill in your API keys.
    echo.
    pause
    exit /b 1
)

:: Run Vigil
echo.
echo Starting Vigil...
echo.
python vigil.py

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Vigil exited with an error.
    pause
)
