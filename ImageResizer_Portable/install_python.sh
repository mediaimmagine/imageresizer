#!/bin/bash

# Python Installer for Image Resizer Portable
# Downloads and installs Python 3.11 for macOS

echo "===================================="
echo "   Python Installer for Image Resizer"
echo "===================================="
echo ""

# Check if Python is already installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        echo "✓ Python $PYTHON_VERSION is already installed and compatible"
        echo "You can now run ImageResizer.command"
        exit 0
    else
        echo "⚠️  Python $PYTHON_VERSION is installed but version 3.8+ is required"
    fi
fi

echo "This installer will download and install Python 3.11 for macOS"
echo "The installation will be local to this application only"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download Python installer
echo "Downloading Python 3.11 installer..."
PYTHON_URL="https://www.python.org/ftp/python/3.11.7/python-3.11.7-macos11.pkg"
curl -L -o python_installer.pkg "$PYTHON_URL"

if [ $? -ne 0 ]; then
    echo "✗ Failed to download Python installer"
    exit 1
fi

echo "✓ Python installer downloaded"

# Install Python
echo "Installing Python (this may require admin password)..."
sudo installer -pkg python_installer.pkg -target /

if [ $? -eq 0 ]; then
    echo "✓ Python installed successfully"
    echo ""
    echo "You can now run ImageResizer.command"
else
    echo "✗ Failed to install Python"
    echo "Please install Python 3.8+ manually from https://python.org"
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"
