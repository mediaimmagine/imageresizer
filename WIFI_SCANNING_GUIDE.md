# WiFi Network Scanning on macOS - Complete Guide

## The Challenge

Modern macOS (especially recent versions) has **restricted access** to WiFi scanning APIs due to privacy and security concerns. The old `airport` command-line utility is deprecated and no longer returns network data.

## Solutions

### Method 1: Wireless Diagnostics App (Easiest - No coding required)

1. **Open Wireless Diagnostics:**
   - Hold the **Option** key and click the WiFi icon in the menu bar
   - Select "Open Wireless Diagnostics"
   - OR run: `open /System/Library/CoreServices/Applications/Wireless\ Diagnostics.app`

2. **Perform a scan:**
   - In the app, go to **Window** → **Scan**
   - You'll see all nearby WiFi networks with SSID, signal strength, channel, and security type
   - Click **Export** to save the data

3. **View the scan results:**
   - The app displays a table with all networks
   - Shows BSSID, SSID, Signal (RSSI), Channel, Security type, and more

### Method 2: wdutil (Command Line - Requires Sudo)

```bash
# Run the provided script
./scan_real_wifi.sh

# Or manually:
sudo wdutil dump
```

**Note:** This requires administrator password.

### Method 3: Use the Created Python Visualization Tool

The `wifi_coverage_scanner.py` tool I created works with real network data. To use it with real networks:

1. **Get network data from Wireless Diagnostics:**
   - Export scan data from Wireless Diagnostics (Method 1)
   - Or manually enter network information

2. **Run the visualizer:**
   ```bash
   python3 wifi_coverage_scanner.py
   ```

### Method 4: Check What's Actually Possible Without Sudo

Let me create a final script that tries everything possible:

```bash
python3 wifi_scanner_final.py
```

## Current Status on Your Mac

- ✅ WiFi is **enabled** (confirmed via `networksetup`)
- ❌ Airport utility is **deprecated** and not returning network data
- ❌ You are **not currently connected** to a WiFi network
- ⚠️ Terminal needs **network permissions** in System Preferences

## To Enable Real Network Scanning

### Step 1: Grant Network Permissions
1. Go to **System Preferences** (or **System Settings** on newer macOS)
2. **Security & Privacy** → **Privacy** tab
3. Select **Network** from the left sidebar
4. Ensure **Terminal** (or your terminal app) has a checkmark

### Step 2: Connect to WiFi or Get Near Networks
- Make sure you're in range of WiFi networks
- You can be disconnected from WiFi but still scan nearby networks

### Step 3: Use Wireless Diagnostics (Recommended)
- This is the official Apple method that always works
- Provides the most detailed information

## Sample Network Visualization

Even without real network data, the tool can create beautiful visualizations. Here's what it shows:

1. **Signal Strength Chart** - Bar chart with color-coded signal strengths
2. **Channel Distribution** - Bar chart showing which channels are used
3. **Coverage Map** - 2D visualization of network coverage areas
4. **Network Details Table** - Top 10 networks with full information

## Files Created

- `wifi_coverage_scanner.py` - Main visualization tool (works with real or sample data)
- `wifi_real_scanner.py` - Attempts to scan real networks
- `wifi_scanner_final.py` - Comprehensive scanner
- `scan_real_wifi.sh` - Bash script for wdutil scanning
- `wifi_swift_scanner.swift` - Swift-based scanner (requires Xcode/toolchain fix)

## Recommended Workflow

1. **For immediate scanning:** Use Wireless Diagnostics app
2. **For automation:** Run `./scan_real_wifi.sh` (requires sudo)
3. **For visualization:** Get data from step 1 or 2, then run `python3 wifi_coverage_scanner.py`

## Next Steps

Would you like me to:

1. Create a script that reads Wireless Diagnostics export files?
2. Build a GUI wrapper around the scanning functionality?
3. Focus on making the visualization work with your current connectivity?

Let me know how you'd like to proceed!








