#!/usr/bin/env python3
"""
Create an improved portable version that ensures all features work correctly
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def create_improved_portable():
    """Create an improved portable version with all features"""
    print("Creating improved portable version...")
    
    # Create portable directory
    portable_dir = Path("ImageResizer_Portable_Improved")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # Copy the exact same image_resizer.py file
    shutil.copy2("image_resizer.py", portable_dir)
    shutil.copy2("requirements_image_resizer.txt", portable_dir)
    
    # Create a better launcher that ensures all dependencies
    launcher_content = '''#!/bin/bash

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

if [ "$(printf '%s\\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
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
'''
    
    launcher_path = portable_dir / "ImageResizer.command"
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    os.chmod(launcher_path, 0o755)
    
    # Create a simple test script
    test_content = '''#!/bin/bash
echo "Testing Image Resizer Portable..."
cd "$(dirname "$0")"
python3 -c "
import sys
print('Python version:', sys.version)
try:
    import tkinter
    print('✓ Tkinter available')
except ImportError:
    print('✗ Tkinter not available')
try:
    import PIL
    print('✓ Pillow available:', PIL.__version__)
except ImportError:
    print('✗ Pillow not available')
try:
    from PIL import Image, ImageTk, ImageDraw
    print('✓ All PIL modules available')
except ImportError as e:
    print('✗ PIL import error:', e)
"
'''
    
    test_path = portable_dir / "test_requirements.sh"
    with open(test_path, 'w') as f:
        f.write(test_content)
    
    os.chmod(test_path, 0o755)
    
    # Create README
    readme_content = '''# Image Resizer - Improved Portable Version

This is the exact same Image Resizer as the Windows version, but packaged for macOS portability.

## Features (Same as Windows Version)
- ✅ Smart resizing with aspect ratio preservation
- ✅ Interactive cropping with manual positioning
- ✅ Multiple output formats (JPG, PNG, WebP)
- ✅ Quality control with real-time preview
- ✅ Web presets (2K, Full HD, HD, Web, Instagram, Thumbnail)
- ✅ Copyright detection and warnings
- ✅ Auto-prefix file naming (trieste@news_)
- ✅ Professional GUI with preview panel

## Quick Start
1. Double-click `ImageResizer.command`
2. If Python is not installed, install it from https://python.org
3. The app will automatically install required packages

## Test Requirements
Run `test_requirements.sh` to check if all dependencies are available.

## Troubleshooting
- If the app doesn't start, run `test_requirements.sh` first
- Make sure Python 3.8+ is installed
- Check that you have internet connection for package installation

This portable version is identical to the Windows version in functionality.
'''
    
    with open(portable_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"✓ Improved portable version created: {portable_dir}")
    return portable_dir

def main():
    """Main function"""
    print("Creating improved portable version...")
    
    portable_dir = create_improved_portable()
    
    print()
    print("====================================")
    print("   Improved Portable Version Ready!")
    print("====================================")
    print()
    print(f"Directory: {portable_dir}")
    print()
    print("To test:")
    print(f"1. cd {portable_dir}")
    print("2. ./test_requirements.sh")
    print("3. ./ImageResizer.command")
    print()
    print("This version ensures all features work correctly!")

if __name__ == "__main__":
    main()









