#!/bin/bash

# Image Resizer Portable Launcher
# Compatible with macOS 10.15+ and iOS 13+ (2020+)

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set up environment
export PYTHONPATH="$SCRIPT_DIR/lib:$PYTHONPATH"
export PATH="$SCRIPT_DIR/bin:$PATH"

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    echo "Or use the included Python installer in the bin/ directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8+ is required, but found $PYTHON_VERSION"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Install required packages if not available
$PYTHON_CMD -c "import PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    $PYTHON_CMD -m pip install --user --upgrade pip
    $PYTHON_CMD -m pip install --user Pillow>=10.0.0
fi

# Launch the application
cd "$SCRIPT_DIR"
$PYTHON_CMD image_resizer.py "$@"
