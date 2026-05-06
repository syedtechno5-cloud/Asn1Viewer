@echo off
REM ASN.1 Viewer Build Script for Windows
REM This script sets up the environment and builds the executable

echo ================================================
echo ASN.1 Viewer - Windows Build Script
echo ================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller asn1_viewer.spec

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build completed successfully!
echo Executable location: dist\ASN1Viewer\ASN1Viewer.exe
echo ================================================
echo.
pause
