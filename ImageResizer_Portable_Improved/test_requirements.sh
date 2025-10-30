#!/bin/bash
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
