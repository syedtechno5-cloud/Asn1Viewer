#!/usr/bin/env bash
# Build script for macOS and Linux
# Produces: dist/ASN1Viewer  and  dist/asn1viewcli

set -euo pipefail

echo "================================================"
echo " ASN.1 Viewer v1.1.0 — Build Script"
echo " Platform: $(uname -s)"
echo "================================================"
echo ""

# ── Check Python ─────────────────────────────────────────────────────────── #

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.8+ first."
    exit 1
fi

PYTHON=python3
PIP="$PYTHON -m pip"
PYVER=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python $PYVER found: $($PYTHON --version)"

# ── Linux: install system Qt dependencies ────────────────────────────────── #

if [[ "$(uname -s)" == "Linux" ]]; then
    echo ""
    echo "Installing Qt system dependencies (requires sudo)..."
    sudo apt-get update -qq 2>/dev/null || true
    sudo apt-get install -y \
        libxkbcommon-x11-0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xinerama0 \
        libxcb-xfixes0 \
        libxcb-cursor0 \
        libegl1 \
        libgl1 2>/dev/null || echo "  (apt-get not available or packages already installed)"
fi

# ── Install Python dependencies ───────────────────────────────────────────── #

echo ""
echo "Installing Python dependencies..."
$PIP install --upgrade pip --quiet
$PIP install -r requirements.txt --quiet
$PIP install pyinstaller --quiet

# ── Build ─────────────────────────────────────────────────────────────────── #

echo ""
echo "Building executables..."
$PYTHON -m PyInstaller asn1_viewer.spec --noconfirm

# ── Set permissions ───────────────────────────────────────────────────────── #

chmod +x dist/ASN1Viewer dist/asn1viewcli

# ── Package ───────────────────────────────────────────────────────────────── #

echo ""
PLATFORM=$(uname -s)

if [[ "$PLATFORM" == "Darwin" ]]; then
    ARCHIVE="ASN1Viewer-macOS-x64.zip"
    zip -r "$ARCHIVE" dist/ASN1Viewer.app dist/asn1viewcli
    echo "Packaged: $ARCHIVE"
else
    ARCHIVE="ASN1Viewer-Linux-x64.tar.gz"
    tar -czf "$ARCHIVE" -C dist ASN1Viewer asn1viewcli
    echo "Packaged: $ARCHIVE"
fi

# ── Done ──────────────────────────────────────────────────────────────────── #

echo ""
echo "================================================"
echo " Build complete!"
echo ""
if [[ "$PLATFORM" == "Darwin" ]]; then
    echo "  GUI:  dist/ASN1Viewer.app"
else
    echo "  GUI:  dist/ASN1Viewer"
fi
echo "  CLI:  dist/asn1viewcli"
echo "  Archive: $ARCHIVE"
echo "================================================"
