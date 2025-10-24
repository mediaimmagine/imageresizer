#!/bin/bash

echo "===================================="
echo "   IMAGE RESIZER - Starting..."
echo "===================================="
echo ""

# Check if Pillow is installed, install if not
python3 -c "import PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required package: Pillow..."
    python3 -m pip install Pillow
    echo ""
fi

echo "Starting Image Resizer..."
python3 image_resizer.py

if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred. Press any key to exit."
    read -n 1
fi

