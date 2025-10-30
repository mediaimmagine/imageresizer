#!/bin/bash
echo "=============================================================="
echo "Real WiFi Networks Detected on Your Mac"
echo "=============================================================="
echo ""
echo "📡 Currently Connected Network:"
networksetup -getairportnetwork en0
echo ""
echo "=============================================================="
echo "📊 All Nearby WiFi Networks (SSIDs):"
echo "=============================================================="

# Extract SSIDs
SSIDS=$(system_profiler SPAirPortDataType | grep -E "^[[:space:]]{12}[A-Z]" | sed 's/^[[:space:]]*//' | sed 's/:$//' | sort | uniq)

COUNT=1
for ssid in $SSIDS; do
    printf "  %2d. %s\n" $COUNT "$ssid"
    COUNT=$((COUNT+1))
done

TOTAL=$(echo "$SSIDS" | wc -l | xargs)
echo ""
echo "=============================================================="
echo "Total unique SSIDs: $TOTAL"
echo "=============================================================="

echo ""
echo "✨ Tip: Run 'python3 wifi_coverage_scanner.py' to create"
echo "   a visual coverage diagram with these networks!"
echo ""



