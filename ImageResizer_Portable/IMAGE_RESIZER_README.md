# 🖼️ Image Resizer & Web Optimizer

A simple, cross-platform GUI application for resizing images with web optimization features.

## 📐 Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│        🖼️ Image Resizer & Web Optimizer                     │
├──────────────────────┬──────────────────────────────────────┤
│  CONTROLS            │  PREVIEW PANEL                       │
│                      │                                      │
│  📁 Upload Image     │  📸 Preview                          │
│  [Browse...]         │                                      │
│                      │  📐 Dimensions: 1920 x 1080 px       │
│  ⚙️ Resize Settings   │  📊 Estimated Size: 245.3 KB        │
│  Width: [1920] px    │  🎚️ Quality: 85%                     │
│  Height: [1080] px   │                                      │
│  🔒 Keep aspect ratio│  ┌────────────────────────────┐      │
│                      │  │                            │      │
│  Quality: [====85%]  │  │    [Resized Image]         │      │
│                      │  │      Preview Here          │      │
│  🌐 Web Presets      │  │                            │      │
│  [2K] [Full HD]      │  │                            │      │
│  [HD] [Web]          │  └────────────────────────────┘      │
│  [Instagram] [Thumb] │                                      │
│                      │                                      │
│  ℹ️ Original Info     │                                      │
│                      │                                      │
│  [🔄 Update Preview] │                                      │
│  [💾 Save Image]     │                                      │
└──────────────────────┴──────────────────────────────────────┘
```

## ✨ Features

- **Cross-Platform**: Works on both Windows and Mac
- **User-Friendly GUI**: Simple and intuitive split-panel interface
- **Embedded Preview**: Live preview panel inside the GUI
- **Real-time Info**: See dimensions and estimated file size instantly
- **Aspect Ratio Lock**: Maintain image proportions automatically
- **Quality Control**: Quick presets (30%, 50%, 85%) and slider for fine control
- **Output Format Selection**: Choose JPG, PNG, or WebP format
- **Copyright Metadata Detection**: Shows **RED WARNING** if image contains copyright information
- **Web Presets**: Quick buttons for common web sizes including 1024x683 and 2048x1366
- **Multiple Input Formats**: Support for JPG, PNG, WebP, BMP, GIF
- **File Size Optimization**: Reduce file size while maintaining quality
- **Auto-Prefix**: Saves files with "trieste@news_" prefix

## 📋 Requirements

- Python 3.7 or higher
- Pillow library (will be auto-installed)

## 🚀 Installation & Usage

### Windows

1. **Easy Method**: Double-click `run_image_resizer.bat`
   - The script will automatically install dependencies and launch the app

2. **Manual Method**:
   ```bash
   pip install Pillow
   python image_resizer.py
   ```

### Mac / Linux

1. **Easy Method**: Make the script executable and run it
   ```bash
   chmod +x run_image_resizer.sh
   ./run_image_resizer.sh
   ```

2. **Manual Method**:
   ```bash
   pip3 install Pillow
   python3 image_resizer.py
   ```

## 🎯 How to Use

1. **Upload Image**: Click "Browse..." to select your image (preview appears automatically)
2. **Set Dimensions**: 
   - Enter desired width and height in the left panel
   - Check "Keep aspect ratio" to maintain proportions
3. **Adjust Quality**: 
   - Use quick preset buttons: **30% (Small)**, **50% (Medium)**, **85% (High)**
   - Or use the slider for custom quality (1-100%)
   - Default is 50%
4. **Choose Output Format**:
   - **JPG/JPEG**: Best for photos, lossy compression
   - **PNG**: Lossless, supports transparency
   - **WebP**: Modern format, smallest file sizes
5. **Use Presets** (optional): Click preset buttons for common sizes:
   - 2K (2048x1366) - High resolution web
   - Full HD (1920x1080) - Standard HD
   - HD (1280x720) - Smaller HD
   - Web (1024x683) - Optimized web size
   - Instagram Square (1080x1080) - Social media
   - Thumbnail (400x300) - Small preview
6. **Preview**: The right panel shows a live preview with:
   - Actual image preview (scaled to fit)
   - Dimensions (width x height)
   - Estimated file size
   - Quality percentage
   - **RED COPYRIGHT WARNING** (if image contains copyright metadata)
7. **Update**: Click "Update Preview" to refresh after changing settings
8. **Save**: Click "Save Resized Image" and choose location
   - Files are automatically saved with "trieste@news_" prefix

## 🌐 Web Optimization Tips

### For Websites
- **Hero Images**: 1920x1080 or 1280x720, Quality 80-85%
- **Thumbnails**: 400x300 or 300x300, Quality 75-80%
- **Blog Images**: 1200x800, Quality 80%

### Format Recommendations

**JPG/JPEG**:
- Best for: Photographs, images with gradients
- Pros: Widely supported, good compression
- Cons: Lossy, no transparency
- Recommended quality: 50-85%

**PNG**:
- Best for: Graphics, logos, images with transparency
- Pros: Lossless, supports transparency
- Cons: Larger file sizes
- Note: Quality slider controls compression level

**WebP**:
- Best for: Modern websites prioritizing performance
- Pros: Best compression, supports transparency
- Cons: Limited support in older browsers
- Recommended quality: 50-80%

### File Size Goals
- **Above the fold**: < 200 KB
- **Thumbnails**: < 50 KB
- **Background images**: < 300 KB

## 🎨 Supported Formats

### Input Formats
- JPEG/JPG
- PNG
- BMP
- GIF
- WebP

### Output Formats
- JPEG (with quality control)
- PNG (optimized)
- WebP (with quality control)

## 📊 Features in Detail

### Aspect Ratio Lock
When enabled, changing width automatically adjusts height (and vice versa) to maintain the original image proportions.

### Quality Control

**Quick Presets** (one-click):
- **30% (Small)**: Maximum compression, smallest file size - good for thumbnails
- **50% (Medium)**: Balanced compression - **DEFAULT** - good for web images
- **85% (High)**: Minimal compression, high quality - good for featured images

**Slider** (custom):
- **90-100%**: Highest quality, larger file size
- **80-90%**: Excellent quality, good compression
- **70-80%**: Good quality, smaller files
- **50-70%**: Moderate quality, good for web
- **30-50%**: Lower quality, very small files
- **Below 30%**: Noticeable quality loss, use only for thumbnails

### Embedded Preview Panel
Shows exactly how your resized image will look before saving, displayed in a dedicated panel on the right side of the window. The preview includes:
- Visual preview of the resized image (scaled to fit the panel)
- Real-time dimensions display
- Estimated file size (based on JPEG compression)
- Quality percentage
- Scrollable view for large images

### Copyright Detection & Warning
**Automatic copyright detection** protects you from using protected images:
- **Scans image metadata** for copyright information (EXIF, PNG metadata)
- **RED WARNING displayed** prominently if copyright is detected
- Shows copyright holder information
- Alerts you to potential licensing issues
- Checks for: Copyright tags, Artist info, Creator metadata

**Warning Format:**
```
WARNING: COPYRIGHT PROTECTED IMAGE
© 2024 Photographer Name / Copyright Notice
```

**Important**: Even without metadata, images may still be copyrighted. Always verify usage rights!

## 🔧 Technical Details

- **Resampling Method**: LANCZOS (highest quality)
- **Optimization**: Automatic for PNG and JPEG
- **RGBA Handling**: Automatic conversion for JPEG compatibility
- **Memory Efficient**: Streams large images properly

## 🐛 Troubleshooting

### "No module named 'PIL'" Error
Run: `pip install Pillow` (Windows) or `pip3 install Pillow` (Mac)

### GUI Doesn't Appear
Make sure you have tkinter installed:
- **Windows**: Included with Python
- **Mac**: Included with Python
- **Linux**: `sudo apt-get install python3-tk`

### Image Won't Load
Ensure your image file is:
- Not corrupted
- In a supported format
- Readable (check file permissions)

## 📝 License

Free to use for personal and commercial projects.

## 💡 Tips

1. **Always preview** before saving to check quality
2. **Use quick presets** for fast quality selection:
   - **30%** for small thumbnails
   - **50%** (default) for general web use
   - **85%** for high-quality featured images
3. **Use PNG** for images with transparency
4. **Keep aspect ratio** unless you specifically need different proportions
5. **Save original** before experimenting with settings
6. **Adjust slider** for fine-tuning if presets don't match your needs

## 🚀 Quick Start Examples

### Resize for Instagram Post
1. Upload your image (preview appears automatically)
2. Click "Instagram (1080x1080)" preset
3. Click "85% (High)" quality preset button
4. Check the preview panel on the right for file size estimate
5. Click "Save Resized Image"

### Optimize Large Photo for Web (1024x683)
1. Upload high-res photo
2. Click "Web (1024x683)" preset
3. Use default 50% quality or click "85% (High)" for better quality
4. Preview shows the optimized result with estimated file size
5. Save as JPG

### Create High-Res Web Image (2048x1366)
1. Upload your image
2. Click "2K (2048x1366)" preset
3. Click "85% (High)" quality preset button
4. Check preview to ensure quality is maintained
5. Save for high-resolution web use

### Create Thumbnail
1. Upload image
2. Click "Thumbnail (400x300)" preset
3. Click "30% (Small)" quality preset button for smallest file size
4. Preview panel shows how it looks at small size
5. Save

---

**Enjoy resizing!** 🎨📸

