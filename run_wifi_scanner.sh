#!/bin/bash
# Quick start script for WiFi Coverage Scanner

echo "WiFi Coverage Scanner"
echo "===================="
echo ""

# Check if dependencies are installed
python3 -c "import matplotlib, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements_wifi_scanner.txt
fi

# Run the scanner
python3 wifi_coverage_scanner.py

echo ""
echo "Done! Check the generated wifi_coverage.png file."








