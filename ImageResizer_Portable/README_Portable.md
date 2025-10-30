# Image Resizer - Portable Version

A portable image resizing application for macOS with iOS compatibility.

## What's Included

### macOS Version
- **ImageResizer.command** - Main launcher (double-click to run)
- **install_python.sh** - Python installer for systems without Python
- **image_resizer.py** - Main application
- **iOS_Version/** - iOS-compatible version

### iOS Version
- **image_resizer_ios.py** - Pythonista-compatible version
- **README_iOS.md** - iOS-specific instructions

## System Requirements

### macOS
- macOS 10.15 (Catalina) or later
- Python 3.8+ (installer included if needed)
- Intel or Apple Silicon Mac

### iOS
- iOS 13.0 or later (compatible with devices from 2020+)
- Pythonista app from App Store
- iPhone or iPad

## Quick Start

### For macOS:
1. Double-click `ImageResizer.command`
2. If Python is not installed, run `install_python.sh` first
3. Select an image and resize!

### For iOS:
1. Install Pythonista from App Store
2. Copy `iOS_Version/image_resizer_ios.py` to Pythonista
3. Run the script in Pythonista

## Features

- **Smart Resizing**: Maintain aspect ratios or crop to fit
- **Multiple Formats**: JPG, PNG, WebP support
- **Quality Control**: Adjustable compression settings
- **Web Presets**: Common sizes for web use
- **Batch Processing**: Process multiple images
- **Copyright Detection**: Warns about protected images
- **Interactive Cropping**: Drag to position crop areas

## File Structure

```
ImageResizer_Portable/
├── ImageResizer.command          # Main launcher
├── install_python.sh             # Python installer
├── image_resizer.py              # Main application
├── requirements_image_resizer.txt # Dependencies
├── bin/                          # Python binaries (if needed)
├── lib/                          # Python libraries
├── images/                       # Sample images
├── output/                       # Default output directory
└── iOS_Version/                  # iOS-compatible version
    ├── image_resizer_ios.py
    └── README_iOS.md
```

## Troubleshooting

### macOS Issues
- **"Python not found"**: Run `install_python.sh` or install Python 3.8+ manually
- **"Permission denied"**: Make sure the .command file is executable
- **"Module not found"**: The launcher will automatically install required packages

### iOS Issues
- **App won't run**: Make sure you have Pythonista 3.0+ installed
- **Can't access Photos**: Grant permission when prompted
- **Script errors**: Check that you copied the complete file

## Compatibility

This portable version is designed to work on:
- macOS 10.15+ (Catalina, Big Sur, Monterey, Ventura, Sonoma, Sequoia)
- iOS 13.0+ (compatible with devices from 2020 onwards)
- Both Intel and Apple Silicon Macs
- iPhone and iPad devices

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure your system meets the requirements
3. Try running the Python installer if needed

## Version History

- v1.0.0 - Initial portable release
  - macOS app bundle support
  - iOS Pythonista compatibility
  - Universal binary for Intel/Apple Silicon
  - Automatic dependency management
