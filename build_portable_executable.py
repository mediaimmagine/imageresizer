#!/usr/bin/env python3
"""
Build a portable executable for macOS using PyInstaller
This creates a standalone app that doesn't rely on system Tkinter
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create a PyInstaller spec file for the image resizer"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['image_resizer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageResizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
    app=Bundle(
        exe,
        name='ImageResizer',
        icon=None,
        bundle_identifier='com.imageresizer.app',
        version='1.0.0',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Image Files',
                    'CFBundleTypeRole': 'Viewer',
                    'LSItemContentTypes': ['public.image'],
                    'CFBundleTypeExtensions': ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp']
                }
            ]
        }
    )
)
'''
    
    with open('image_resizer.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building portable executable...")
    
    try:
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=ImageResizer",
            "--add-data=requirements_image_resizer.txt:.",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL.Image",
            "--hidden-import=PIL.ImageTk",
            "--hidden-import=tkinter",
            "--hidden-import=tkinter.filedialog",
            "--hidden-import=tkinter.messagebox",
            "--hidden-import=tkinter.ttk",
            "--osx-bundle-identifier=com.imageresizer.app",
            "image_resizer.py"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        print("Build completed successfully!")
        print("Executable created in: dist/ImageResizer.app")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def create_launcher_script():
    """Create a launcher script for the executable"""
    launcher_content = '''#!/bin/bash

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
'''
    
    with open('launch_image_resizer.sh', 'w') as f:
        f.write(launcher_content)
    
    os.chmod('launch_image_resizer.sh', 0o755)
    print("Created launcher script: launch_image_resizer.sh")

def main():
    print("Building Portable Image Resizer for macOS")
    print("=" * 50)
    
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("Error: This script is designed for macOS only")
        sys.exit(1)
    
    # Check if image_resizer.py exists
    if not os.path.exists('image_resizer.py'):
        print("Error: image_resizer.py not found in current directory")
        sys.exit(1)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("Error: Could not install PyInstaller")
        sys.exit(1)
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        print("\n" + "=" * 50)
        print("SUCCESS! Portable executable created!")
        print("=" * 50)
        print("To run the application:")
        print("1. Double-click on dist/ImageResizer.app")
        print("2. Or run: ./launch_image_resizer.sh")
        print("\nThe executable is completely portable and includes:")
        print("- Python runtime")
        print("- All dependencies (Pillow, Tkinter)")
        print("- The complete Image Resizer application")
        print("\nYou can copy the entire dist/ImageResizer.app folder")
        print("to any Mac and it will run without installation!")
        
        # Create launcher script
        create_launcher_script()
        
    else:
        print("Build failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()









