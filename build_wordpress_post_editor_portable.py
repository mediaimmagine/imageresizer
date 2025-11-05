#!/usr/bin/env python3
"""
Build script for creating a portable macOS app bundle of WordPress Post Editor
Compatible with macOS Ventura 13.7.8+ (Intel and Apple Silicon)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def check_dependencies():
    """Check and install required dependencies"""
    print("Checking dependencies...")
    required_packages = [
        "PyQt5>=5.15.0",
        "requests>=2.28.0",
        "Pillow>=10.0.0",
    ]
    
    for package in required_packages:
        package_name = package.split(">=")[0].split("==")[0]
        try:
            __import__(package_name.lower().replace("-", "_"))
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"Installing {package_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package_name} installed successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package_name}")
                return False
    return True

def create_app_bundle():
    """Create the macOS app bundle"""
    print("\nCreating macOS app bundle...")
    
    import platform
    arch = platform.machine().lower()
    target_arch = None
    if arch in ("arm64", "aarch64"):
        target_arch = "arm64"
    elif arch in ("x86_64", "amd64"):
        target_arch = "x86_64"

    # Check if app_icon.icns exists, if not create a placeholder
    icon_file = "app_icon.icns"
    if not os.path.exists(icon_file):
        print(f"Warning: {icon_file} not found, app will use default icon")
        icon_file = None

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--windowed",
        "--name=WordPressPostEditor",
        "--add-data=requirements_image_resizer.txt:." if os.path.exists("requirements_image_resizer.txt") else "",
        "--add-data=mediaimmagine_logo.png:." if os.path.exists("mediaimmagine_logo.png") else "",
        "--add-data=mediaimmagine_logo_white.png:." if os.path.exists("mediaimmagine_logo_white.png") else "",
        # PyQt5 imports
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.sip",
        # Requests imports
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        # PIL imports
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        # Exclude heavy/unused modules
        "--exclude-module=PyQt5.QtWebEngine",
        "--exclude-module=PyQt5.QtWebEngineCore",
        "--exclude-module=PyQt5.QtWebEngineWidgets",
        "--exclude-module=PyQt5.QtQuick",
        "--exclude-module=PyQt5.QtQuickWidgets",
        "--exclude-module=PyQt5.QtQuick3D",
        "--exclude-module=PyQt5.Qt3DCore",
        "--exclude-module=PyQt5.Qt3DRender",
        "--exclude-module=PyQt5.Qt3DInput",
        "--osx-bundle-identifier=com.mediaimmagine.wordpressposteditor",
    ]
    
    # Add icon if available
    if icon_file:
        cmd.insert(cmd.index("--name=WordPressPostEditor") + 1, f"--icon={icon_file}")
    
    # Remove empty strings from cmd
    cmd = [c for c in cmd if c]
    
    if target_arch:
        cmd.append(f"--target-architecture={target_arch}")
    
    cmd.append("wordpress_post_editor.py")
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✓ App bundle created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create app bundle: {e}")
        return False

def create_portable_package():
    """Create a portable package with all necessary files"""
    print("\nCreating portable package...")
    
    portable_dir = Path("WordPressPostEditor_Portable")
    
    # Clean up existing directory
    if portable_dir.exists():
        print(f"Removing existing {portable_dir}...")
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir(exist_ok=True)
    
    # Copy app bundle
    app_bundle = Path("dist/WordPressPostEditor.app")
    if app_bundle.exists():
        print(f"Copying app bundle to {portable_dir}...")
        shutil.copytree(app_bundle, portable_dir / "WordPressPostEditor.app")
        print("✓ App bundle copied")
    else:
        print("✗ App bundle not found in dist/WordPressPostEditor.app")
        return False
    
    # Create launcher script
    launcher_content = """#!/bin/bash
# WordPress Post Editor Launcher
# Compatible with macOS Ventura 13.7.8+

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PATH="$SCRIPT_DIR/WordPressPostEditor.app"

if [ -d "$APP_PATH" ]; then
    open "$APP_PATH"
else
    echo "Error: WordPressPostEditor.app not found in $SCRIPT_DIR"
    exit 1
fi
"""
    
    launcher_path = portable_dir / "WordPressPostEditor.command"
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    os.chmod(launcher_path, 0o755)
    print("✓ Launcher script created")
    
    # Create README
    readme_content = """# WordPress Post Editor - Portable macOS Version

## Requirements
- macOS Ventura 13.7.8 or later
- Compatible with Intel and Apple Silicon Macs

## Installation
No installation required! This is a portable application.

## Usage
1. Double-click `WordPressPostEditor.command` to launch the app
2. Or double-click `WordPressPostEditor.app` directly

## Features
- Create and edit WordPress posts offline
- Publish to multiple WordPress sites simultaneously
- Upload featured images
- Rich text editor with formatting tools
- Support for WordPress REST API and MiniOrange authentication
- Schedule posts for future publication

## Supported Sites
- Trieste News (MiniOrange authentication)
- Gorizia Oggi
- Udine Oggi
- Venezia Orientale

## Troubleshooting
If the app doesn't launch:
1. Right-click the `.command` file and select "Open"
2. If prompted about security, go to System Preferences → Security & Privacy → Allow

## Notes
- Settings are stored in `~/.imageresizer/wp_settings.json`
- Drafts are stored locally in the app
- First launch may take a few seconds to initialize

## Support
For issues or questions, contact Media Immagine support.

---
Version: 1.0
Compatible with: macOS Ventura 13.7.8+
"""
    
    readme_path = portable_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)
    print("✓ README created")
    
    # Create zip file
    print("\nCreating distribution package...")
    zip_name = "WordPressPostEditor_Portable_macOS.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    try:
        shutil.make_archive(
            zip_name.replace(".zip", ""),
            "zip",
            portable_dir.parent,
            portable_dir.name
        )
        print(f"✓ Distribution package created: {zip_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to create zip file: {e}")
        return False

def main():
    print("=" * 60)
    print("   Building Portable WordPress Post Editor")
    print("   macOS Ventura 13.7.8+ Compatible")
    print("=" * 60)
    print()
    
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("Error: This script is designed for macOS only")
        sys.exit(1)
    
    # Check if wordpress_post_editor.py exists
    if not os.path.exists('wordpress_post_editor.py'):
        print("Error: wordpress_post_editor.py not found in current directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("Error: Failed to install required dependencies")
        sys.exit(1)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("Error: Could not install PyInstaller")
        sys.exit(1)
    
    # Create app bundle
    if not create_app_bundle():
        print("Error: Failed to create app bundle")
        sys.exit(1)
    
    # Create portable package
    if not create_portable_package():
        print("Error: Failed to create portable package")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("   SUCCESS! Portable app created!")
    print("=" * 60)
    print()
    print("Files created:")
    print("• WordPressPostEditor_Portable/ - Portable directory")
    print("• WordPressPostEditor_Portable_macOS.zip - Distribution package")
    print()
    print("To test:")
    print("1. cd WordPressPostEditor_Portable")
    print("2. ./WordPressPostEditor.command")
    print()
    print("The app is completely portable and includes:")
    print("- Python runtime")
    print("- All dependencies (PyQt5, requests, Pillow)")
    print("- The complete WordPress Post Editor application")
    print()
    print("You can copy the entire WordPressPostEditor_Portable folder")
    print("to any Mac (Ventura 13.7.8+) and it will run without installation!")

if __name__ == "__main__":
    main()

