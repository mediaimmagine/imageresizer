#!/usr/bin/env python3
"""
Build script for creating a macOS app bundle of Image Resizer
Compatible with macOS 10.15+ and iOS 13+ (2020+)
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

def create_app_bundle():
    """Create the macOS app bundle"""
    print("Creating macOS app bundle...")
    
    # PyInstaller command for macOS app bundle (PyQt5 app)
    import platform
    arch = platform.machine().lower()
    target_arch = None
    if arch in ("arm64", "aarch64"):
        target_arch = "arm64"
    elif arch in ("x86_64", "amd64"):
        target_arch = "x86_64"

    cmd = [
        "pyinstaller",
        # Use onedir for macOS .app stability (PyQt plugins load reliably)
        "--clean",
        "--noconfirm",
        "--windowed",
        "--name=ImageResizer",
        "--icon=app_icon.icns",  # We'll create this
        "--add-data=requirements_image_resizer.txt:.",
        "--add-data=mediaimmagine_logo_white.png:.",
        # Limit PyQt5 collection to core widgets; exclude heavy/unused modules
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        "--hidden-import=PyQt5.sip",
        "--collect-submodules=PyQt5.QtCore",
        "--collect-submodules=PyQt5.QtGui",
        "--collect-submodules=PyQt5.QtWidgets",
        "--exclude-module=PyQt5.QtWebEngine",
        "--exclude-module=PyQt5.QtWebEngineCore",
        "--exclude-module=PyQt5.QtWebEngineWidgets",
        "--exclude-module=PyQt5.QtQuick",
        "--exclude-module=PyQt5.QtQuickWidgets",
        "--exclude-module=PyQt5.QtQuick3D",
        "--exclude-module=PyQt5.Qt3DCore",
        "--exclude-module=PyQt5.Qt3DRender",
        "--exclude-module=PyQt5.Qt3DInput",
        "--osx-bundle-identifier=com.imageresizer.app",
    ]
    if target_arch:
        cmd.append(f"--target-arch={target_arch}")
    cmd.append("image_resizer.py")
    
    try:
        subprocess.check_call(cmd)
        print("✓ App bundle created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create app bundle: {e}")
        return False


def create_wp_app_bundle():
    """Create the macOS app bundle for the WordPress test variant"""
    print("Creating macOS app bundle (WordPress variant)...")
    import platform
    arch = platform.machine().lower()
    target_arch = None
    if arch in ("arm64", "aarch64"):
        target_arch = "arm64"
    elif arch in ("x86_64", "amd64"):
        target_arch = "x86_64"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--windowed",
        "--name=ImageResizerWP",
        "--icon=app_icon.icns",
        "--add-data=requirements_image_resizer.txt:.",
        "--add-data=mediaimmagine_logo_white.png:.",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        "--hidden-import=PyQt5.sip",
        "--collect-submodules=PyQt5.QtCore",
        "--collect-submodules=PyQt5.QtGui",
        "--collect-submodules=PyQt5.QtWidgets",
        "--osx-bundle-identifier=com.imageresizer.wp",
    ]
    if target_arch:
        cmd.append(f"--target-arch={target_arch}")
    cmd.append("image_resizer_macos_wp.py")

    try:
        subprocess.check_call(cmd)
        print("✓ WP App bundle created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create WP app bundle: {e}")
        return False

def create_app_icon():
    """Create a simple app icon if one doesn't exist"""
    icon_path = Path("app_icon.icns")
    # Prefer the Windows/previous build icon if available
    preferred_icon = Path("dist/ImageResizer.app/Contents/Resources/icon-windowed.icns")
    if preferred_icon.exists():
        try:
            shutil.copy2(preferred_icon, icon_path)
            print("✓ Reused Windows icon (icon-windowed.icns)")
            return True
        except Exception as e:
            print(f"Warning: could not reuse icon-windowed.icns: {e}")
    if icon_path.exists():
        print("✓ App icon already exists")
        return True
    
    print("Creating app icon...")
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        size = 512
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple image resizer icon
        # Background circle
        draw.ellipse([50, 50, size-50, size-50], fill=(52, 152, 219, 255))
        
        # Image frame
        frame_size = 200
        frame_x = (size - frame_size) // 2
        frame_y = (size - frame_size) // 2
        draw.rectangle([frame_x, frame_y, frame_x + frame_size, frame_y + frame_size], 
                      outline=(255, 255, 255, 255), width=8)
        
        # Resize arrows
        arrow_size = 30
        # Right arrow
        draw.polygon([(frame_x + frame_size + 20, frame_y + frame_size//2 - arrow_size//2),
                     (frame_x + frame_size + 20 + arrow_size, frame_y + frame_size//2),
                     (frame_x + frame_size + 20, frame_y + frame_size//2 + arrow_size//2)],
                    fill=(255, 255, 255, 255))
        
        # Save as PNG first
        img.save("app_icon.png")
        
        # Convert to ICNS using sips (macOS built-in tool)
        subprocess.check_call([
            "sips", "-s", "format", "icns", "app_icon.png", 
            "--out", "app_icon.icns"
        ])
        
        # Clean up PNG
        os.remove("app_icon.png")
        
        print("✓ App icon created")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create app icon: {e}")
        return False

def create_info_plist():
    """Create Info.plist for better macOS integration"""
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Image Resizer</string>
    <key>CFBundleIdentifier</key>
    <string>com.imageresizer.app</string>
    <key>CFBundleName</key>
    <string>ImageResizer</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>jpg</string>
                <string>jpeg</string>
                <string>png</string>
                <string>bmp</string>
                <string>gif</string>
                <string>webp</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>Image Files</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
        </dict>
    </array>
</dict>
</plist>"""
    
    with open("ImageResizer.app/Contents/Info.plist", "w") as f:
        f.write(plist_content)
    
    print("✓ Info.plist created")

def main():
    """Main build process"""
    print("====================================")
    print("   Building macOS Image Resizer App")
    print("====================================")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ is required")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("✗ This script should be run on macOS")
        return False
    
    print("✓ Running on macOS")
    
    # Install PyInstaller if needed
    if not check_pyinstaller():
        return False
    
    # Create app icon
    if not create_app_icon():
        print("Warning: Continuing without custom icon")
    
    # Create app bundle
    if not create_app_bundle():
        return False
    
    # Create Info.plist for better integration
    if os.path.exists("dist/ImageResizer.app"):
        os.chdir("dist")
        create_info_plist()
        os.chdir("..")
    
    print()
    print("====================================")
    print("   Build Complete!")
    print("====================================")
    print()
    print("The macOS app bundle has been created in the 'dist' folder.")
    print("You can now:")
    print("1. Copy ImageResizer.app to Applications folder")
    print("2. Double-click to run")
    print("3. Drag and drop image files onto the app icon")
    print()
    print("The app is compatible with:")
    print("- macOS 10.15+ (Catalina and later)")
    print("- Intel and Apple Silicon Macs")
    print("- iOS 13+ devices (via web version)")
    
    return True


def main_wp():
    """Build process for the WordPress variant"""
    print("====================================")
    print("   Building macOS Image Resizer WP App")
    print("====================================")
    print()

    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    if sys.platform != "darwin":
        print("✗ This script should be run on macOS")
        return False
    print("✓ Running on macOS")
    if not check_pyinstaller():
        return False
    if not create_app_icon():
        print("Warning: Continuing without custom icon")
    if not create_wp_app_bundle():
        return False
    if os.path.exists("dist/ImageResizerWP.app"):
        # Write a minimal plist tailored to WP app
        plist_path = "dist/ImageResizerWP.app/Contents/Info.plist"
        plist = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Image Resizer WP</string>
    <key>CFBundleIdentifier</key>
    <string>com.imageresizer.wp</string>
    <key>CFBundleName</key>
    <string>ImageResizerWP</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
        with open(plist_path, "w") as f:
            f.write(plist)
    print("\nWP Build complete (dist/ImageResizerWP.app)")
    return True

if __name__ == "__main__":
    # Support optional arg: --wp to build the WP variant
    if len(sys.argv) > 1 and sys.argv[1] == "--wp":
        success = main_wp()
    else:
        success = main()
    sys.exit(0 if success else 1)

