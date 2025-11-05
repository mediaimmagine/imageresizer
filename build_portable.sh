#!/bin/bash

# Build script for portable Image Resizer
# Creates portable versions for macOS and iOS

echo "===================================="
echo "   Building Portable Image Resizer"
echo "   macOS + iOS Compatible (2020+)"
echo "===================================="
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"
echo ""

# Install required packages
echo "Installing required packages..."
$PYTHON_CMD -m pip install --user --upgrade pip
$PYTHON_CMD -m pip install --user Pillow>=10.0.0

if [ $? -ne 0 ]; then
    echo "Error: Failed to install required packages"
    exit 1
fi

echo "✓ Required packages installed"
echo ""

# Run the portable creation script
echo "Creating portable version..."
$PYTHON_CMD create_portable_mac.py

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================="
    echo "   Build Complete!"
    echo "===================================="
    echo ""
    echo "Portable version created successfully!"
    echo ""
    echo "Files created:"
    echo "• ImageResizer_Portable/ - Portable directory"
    echo "• ImageResizer_Portable_macOS_iOS.zip - Distribution package"
    echo ""
    echo "To test:"
    echo "1. cd ImageResizer_Portable"
    echo "2. ./ImageResizer.command"
    echo ""
    echo "For iOS:"
    echo "1. Install Pythonista from App Store"
    echo "2. Copy iOS_Version/image_resizer_ios.py to Pythonista"
    echo "3. Run in Pythonista"
else
    echo "Error: Build failed"
    exit 1
fi











