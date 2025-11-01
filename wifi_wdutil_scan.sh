#!/bin/bash
# WiFi Scanner using wdutil (requires sudo)

echo "WiFi Network Scanner - Using wdutil"
echo "===================================="
echo ""
echo "NOTE: This will require your administrator password"
echo ""

# Check if we have network interfaces
echo "Checking WiFi interface..."
IFS=$'\n'
for line in $(networksetup -listallhardwareports); do
    if [[ $line == *"Wi-Fi"* ]] || [[ $line == *"AirPort"* ]]; then
        echo "Found: $line"
    fi
done

echo ""
echo "Attempting to scan with wdutil..."
echo "Press Ctrl+C if prompted for password and you want to cancel"
echo ""

# Try wdutil
sudo wdutil dump 2>&1 | head -100

echo ""
echo ""
echo "Alternative: Check Wireless Diagnostics"
echo "Hold Option key and click the WiFi icon, then choose 'Open Wireless Diagnostics'"






