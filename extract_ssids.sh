#!/bin/bash
echo "WiFi Networks Detected:"
echo "======================="
echo ""

system_profiler SPAirPortDataType | grep -A 10 "Other Local Wi-Fi Networks:" | grep -E "^[[:space:]]{8}[A-Z0-9_-]+:" | sed 's/^[[:space:]]*//' | sed 's/:$//' | sort | uniq

echo ""
echo "Summary:"
system_profiler SPAirPortDataType | grep -A 10 "Other Local Wi-Fi Networks:" | grep -E "^[[:space:]]{8}[A-Z0-9_-]+:" | sed 's/^[[:space:]]*//' | sed 's/:$//' | sort | uniq | wc -l | xargs -I {} echo "Total unique SSIDs: {}"
