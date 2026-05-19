@echo off
REM ============================================================
REM  ASN.1 Viewer v1.1.0 — Windows Build Script
REM  Produces: dist\ASN1Viewer.exe  and  dist\asn1viewcli.exe
REM ============================================================

echo ============================================================
echo  ASN.1 Viewer v1.1.0 - Windows Build Script
echo ============================================================
echo.

REM ── Check Python ────────────────────────────────────────────

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.8+ from https://www.python.org/
    echo        Make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo Python found: %%v

REM ── Install dependencies ─────────────────────────────────────

echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip --quiet
if errorlevel 1 ( echo ERROR: pip upgrade failed & pause & exit /b 1 )

python -m pip install -r requirements.txt --quiet
if errorlevel 1 ( echo ERROR: Failed to install requirements & pause & exit /b 1 )

python -m pip install pyinstaller --quiet
if errorlevel 1 ( echo ERROR: Failed to install PyInstaller & pause & exit /b 1 )

REM ── Build ────────────────────────────────────────────────────

echo.
echo Building executables...
python -m PyInstaller asn1_viewer.spec --noconfirm
if errorlevel 1 ( echo ERROR: Build failed & pause & exit /b 1 )

REM ── Package ──────────────────────────────────────────────────

echo.
echo Packaging...
powershell -NoProfile -Command ^
  "Compress-Archive -Force -Path dist\ASN1Viewer.exe, dist\asn1viewcli.exe -DestinationPath ASN1Viewer-Windows-x64.zip"
if errorlevel 1 ( echo WARNING: Packaging failed, executables are still in dist\ )

REM ── Done ─────────────────────────────────────────────────────

echo.
echo ============================================================
echo  Build complete!
echo.
echo   GUI:     dist\ASN1Viewer.exe
echo   CLI:     dist\asn1viewcli.exe
echo   Archive: ASN1Viewer-Windows-x64.zip
echo ============================================================
echo.
pause
