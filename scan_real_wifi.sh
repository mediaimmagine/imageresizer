#!/bin/bash
# Real WiFi Scanner - requires sudo

echo "=================================================="
echo "Real WiFi Network Scanner for macOS"
echo "=================================================="
echo ""
echo "This script will scan for nearby WiFi networks."
echo "It requires administrator privileges."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Scanning with wdutil..."
echo "=================================================="
echo ""

# Use wdutil to get WiFi data
sudo wdutil dump 2>&1 | head -150

echo ""
echo ""
echo "=================================================="
echo "Alternative methods:"
echo "=================================================="
echo ""
echo "1. Use the WiFi menu icon:"
echo "   - Hold Option key and click the WiFi icon"
echo "   - Select 'Open Wireless Diagnostics'"
echo ""
echo "2. Run Wireless Diagnostics directly:"
echo "   open /System/Library/CoreServices/Applications/Wireless\\ Diagnostics.app"
echo ""




