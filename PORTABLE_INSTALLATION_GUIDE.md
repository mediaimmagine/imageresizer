# Image Resizer - Portable Installation Guide

## Overview

This guide will help you create a portable version of Image Resizer that works on:
- **macOS 10.15+** (Catalina and later)
- **iOS 13+** (compatible with devices from 2020 onwards)
- **Intel and Apple Silicon Macs**

## Quick Start

### Option 1: Automated Build (Recommended)

1. **Run the build script:**
   ```bash
   ./build_portable.sh
   ```

2. **The script will:**
   - Check Python installation
   - Install required packages
   - Create portable directory structure
   - Generate macOS launcher
   - Create iOS-compatible version
   - Package everything into a zip file

3. **Result:**
   - `ImageResizer_Portable/` directory
   - `ImageResizer_Portable_macOS_iOS.zip` distribution package

### Option 2: Manual Build

1. **Install Python 3.8+** (if not already installed):
   ```bash
   # Check if Python is installed
   python3 --version
   
   # If not installed, install via Homebrew
   brew install python3
   ```

2. **Install required packages:**
   ```bash
   pip3 install Pillow>=10.0.0
   ```

3. **Run the portable creator:**
   ```bash
   python3 create_portable_mac.py
   ```

## What Gets Created

### Directory Structure
```
ImageResizer_Portable/
├── ImageResizer.command          # Main launcher (double-click to run)
├── install_python.sh             # Python installer for systems without Python
├── image_resizer.py              # Main application
├── requirements_image_resizer.txt # Dependencies
├── README_Portable.md            # Comprehensive documentation
├── bin/                          # Python binaries (if needed)
├── lib/                          # Python libraries
├── images/                       # Sample images
├── output/                       # Default output directory
└── iOS_Version/                  # iOS-compatible version
    ├── image_resizer_ios.py      # Pythonista script
    └── README_iOS.md             # iOS instructions
```

## Usage Instructions

### For macOS Users

1. **Extract the portable package** (if using zip)
2. **Double-click `ImageResizer.command`**
3. **If Python is not installed:**
   - Run `install_python.sh` first
   - Then run `ImageResizer.command`

### For iOS Users

1. **Install Pythonista** from the App Store
2. **Copy `iOS_Version/image_resizer_ios.py`** to Pythonista
3. **Run the script** in Pythonista
4. **Grant photo access** when prompted

## Features

### macOS Version
- ✅ Native macOS app experience
- ✅ Drag-and-drop image support
- ✅ Interactive cropping with visual preview
- ✅ Multiple output formats (JPG, PNG, WebP)
- ✅ Quality adjustment with real-time preview
- ✅ Web presets (HD, Full HD, Instagram, etc.)
- ✅ Copyright detection and warnings
- ✅ Batch processing capabilities

### iOS Version
- ✅ Touch-friendly interface
- ✅ Direct Photos library integration
- ✅ Quick preset buttons
- ✅ Quality slider control
- ✅ Save directly to Photos
- ✅ Compatible with iOS 13+ (2020+ devices)

## System Requirements

### macOS
- **Operating System:** macOS 10.15 (Catalina) or later
- **Python:** 3.8+ (installer included if needed)
- **Architecture:** Intel or Apple Silicon
- **Memory:** 4GB RAM minimum
- **Storage:** 100MB for application + space for images

### iOS
- **Operating System:** iOS 13.0 or later
- **Device:** iPhone or iPad (2020+ models)
- **App:** Pythonista 3.0+ from App Store
- **Storage:** 50MB for app + space for images

## Troubleshooting

### Common macOS Issues

**"Python not found" error:**
```bash
# Solution 1: Run the installer
./install_python.sh

# Solution 2: Install manually
brew install python3
```

**"Permission denied" error:**
```bash
# Make the launcher executable
chmod +x ImageResizer.command
```

**"Module not found" error:**
- The launcher automatically installs required packages
- If it fails, run: `pip3 install Pillow>=10.0.0`

### Common iOS Issues

**App won't run:**
- Ensure Pythonista 3.0+ is installed
- Check that the complete script was copied

**Can't access Photos:**
- Grant permission when prompted
- Check Settings > Privacy > Photos > Pythonista

**Script errors:**
- Verify the complete file was copied
- Check for any missing lines

## Distribution

### Sharing the Portable Version

1. **Create the portable package:**
   ```bash
   ./build_portable.sh
   ```

2. **Share the zip file:**
   - `ImageResizer_Portable_macOS_iOS.zip`
   - Recipients extract and run `ImageResizer.command`

3. **For iOS users:**
   - Share the `iOS_Version/` folder contents
   - Include installation instructions

### File Sizes
- **Portable directory:** ~50MB
- **Zip package:** ~20MB (compressed)
- **iOS version:** ~5KB (script only)

## Advanced Configuration

### Custom Python Installation
If you want to use a specific Python installation:

1. **Edit `ImageResizer.command`:**
   ```bash
   # Change this line:
   PYTHON_CMD="python3"
   
   # To your Python path:
   PYTHON_CMD="/path/to/your/python3"
   ```

### Custom Output Directory
The app saves to `output/` by default. To change:

1. **Edit `image_resizer.py`**
2. **Find the save dialog section**
3. **Modify the default directory**

## Support and Updates

### Getting Help
1. Check this installation guide
2. Review the troubleshooting section
3. Ensure system requirements are met
4. Try the Python installer if needed

### Updating
To update the portable version:
1. Run `./build_portable.sh` again
2. Replace the old portable directory
3. Keep your settings and output files

## Version Compatibility

| macOS Version | iOS Version | Python Version | Status |
|---------------|-------------|----------------|---------|
| 10.15+ | 13.0+ | 3.8+ | ✅ Fully Supported |
| 10.14 | 12.0 | 3.7 | ⚠️ Limited Support |
| < 10.14 | < 12.0 | < 3.7 | ❌ Not Supported |

## License and Legal

This portable version maintains the same license as the original Image Resizer. The iOS version is designed for personal use with Pythonista.

---

**Created for:** macOS 10.15+ and iOS 13+ compatibility (2020+ devices)  
**Last Updated:** 2024  
**Version:** 1.0.0 Portable







