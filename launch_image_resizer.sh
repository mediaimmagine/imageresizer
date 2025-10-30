#!/bin/bash

echo "Starting Image Resizer..."
echo "This is a portable executable version"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Path to the executable
EXECUTABLE_PATH="$SCRIPT_DIR/dist/ImageResizer.app/Contents/MacOS/ImageResizer"

# Check if executable exists
if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "Error: Executable not found at $EXECUTABLE_PATH"
    echo "Please run build_portable_executable.py first"
    exit 1
fi

# Run the executable
echo "Launching Image Resizer..."
"$EXECUTABLE_PATH"
