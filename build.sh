#!/bin/bash
# ASN.1 Viewer Build Script for macOS/Linux

echo "================================================"
echo "ASN.1 Viewer - Build Script"
echo "================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Installing PyInstaller..."
pip install pyinstaller

echo ""
echo "Building executable..."
pyinstaller asn1_viewer.spec

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "================================================"
echo "Build completed successfully!"
echo "Executable location: dist/ASN1Viewer/ASN1Viewer"
echo "================================================"
echo ""
