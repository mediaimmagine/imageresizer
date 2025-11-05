#!/bin/bash
# WordPress Post Editor Launcher for macOS
# Double-click this file to run the app

cd "$(dirname "$0")"
python3 wordpress_post_editor.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Press any key to close..."
    read -n 1
fi

