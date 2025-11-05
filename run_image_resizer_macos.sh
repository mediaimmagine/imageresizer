#!/bin/bash

# Image Resizer - macOS Launcher
# Handles GUI properly without getting stuck

echo "===================================="
echo "   Image Resizer - Starting..."
echo "   macOS Compatible Version"
echo "===================================="
echo ""

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
echo ""

# Install required packages
echo "Installing required packages..."
$PYTHON_CMD -m pip install --user --upgrade pip
$PYTHON_CMD -m pip install --user --upgrade Pillow>=10.0.0

if [ $? -ne 0 ]; then
    echo "Error: Failed to install required packages"
    exit 1
fi

echo "✓ All packages ready"
echo ""

# macOS-specific environment setup
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Configuring for macOS..."
    export TK_SILENCE_DEPRECATION=1
    echo "✓ macOS configuration applied"
fi

echo ""

# Launch the application
echo "Starting Image Resizer..."
echo "Note: The GUI window should appear shortly..."
echo ""

# Run the application
$PYTHON_CMD image_resizer_macos_working.py

echo ""
echo "Image Resizer closed."











