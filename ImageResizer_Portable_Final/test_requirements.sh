#!/bin/bash
echo "Testing Image Resizer Portable - Final Version..."
cd "$(dirname "$0")"

echo "Python version:"
python3 --version

echo ""
echo "Testing imports:"
python3 -c "
import sys
print('Python version:', sys.version)
try:
    import tkinter
    print('✓ Tkinter available')
    # Test basic GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide window
    print('✓ Tkinter GUI test passed')
    root.destroy()
except ImportError as e:
    print('✗ Tkinter not available:', e)
except Exception as e:
    print('✗ Tkinter GUI test failed:', e)

try:
    import PIL
    print('✓ Pillow available:', PIL.__version__)
except ImportError as e:
    print('✗ Pillow not available:', e)

try:
    from PIL import Image, ImageTk, ImageDraw
    print('✓ All PIL modules available')
except ImportError as e:
    print('✗ PIL import error:', e)
"

echo ""
echo "Test complete!"
