#!/bin/bash

# Image Resizer Portable Launcher - Improved Version
# Ensures all features work correctly

echo "===================================="
echo "   Image Resizer Portable - Starting"
echo "===================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to script directory
cd "$SCRIPT_DIR"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8+ is required, but found $PYTHON_VERSION"
    exit 1
fi

# Install/upgrade required packages
echo "Ensuring all required packages are installed..."
$PYTHON_CMD -m pip install --user --upgrade pip
$PYTHON_CMD -m pip install --user --upgrade Pillow>=10.0.0

if [ $? -ne 0 ]; then
    echo "Error: Failed to install required packages"
    exit 1
fi

echo "✓ All packages ready"
echo ""

# Launch the application
echo "Starting Image Resizer..."
$PYTHON_CMD image_resizer.py "$@"
