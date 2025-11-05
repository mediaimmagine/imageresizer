# WiFi Coverage Scanner and Visualizer

A Python tool to scan nearby WiFi networks on macOS and visualize coverage, signal strength, and channel distribution.

## Features

- **Network Scanning**: Detects all nearby WiFi networks
- **Signal Strength Analysis**: Visualizes RSSI values with color-coded indicators
- **Channel Distribution**: Shows which channels networks are using (helps identify interference)
- **Coverage Map**: Simulated 2D visualization of network coverage areas
- **Detailed Table**: Lists network details including SSID, signal strength, channel, and quality

## Installation

1. Install required Python packages:
```bash
pip install -r requirements_wifi_scanner.txt
```

2. Make the script executable:
```bash
chmod +x wifi_coverage_scanner.py
```

## Usage

### Single Scan
```bash
python wifi_coverage_scanner.py
```

### Continuous Scanning
Scan networks every 5 seconds and save multiple coverage diagrams:
```bash
python wifi_coverage_scanner.py --continuous
```

### Custom Interval
Scan every 10 seconds:
```bash
python wifi_coverage_scanner.py --continuous --interval 10
```

## Output

The tool generates a PNG image (`wifi_coverage.png`) with four panels:

1. **Signal Strength Bar Chart**: Shows all networks sorted by signal strength with color-coded bars
2. **Channel Distribution**: Bar chart showing how many networks use each channel
3. **Coverage Map**: 2D visualization of network coverage (simulated positions)
4. **Network Details Table**: Top 10 networks with SSID, signal, channel, and quality indicators

## Signal Strength Guide

- **Excellent** (-50 to -67 dBm): Fast, reliable connection
- **Good** (-67 to -70 dBm): Decent connection, good for most uses
- **Fair** (-70 to -80 dBm): Usable but slower, may have issues
- **Weak** (-80 to -90 dBm): Poor connection, frequent drops
- **Very Weak** (Below -90 dBm): Mostly unusable

## macOS Notes

The tool uses the built-in `airport` utility for scanning. If it's not available, it will generate sample data for demonstration purposes.

To enable the airport utility on modern macOS:
```bash
sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport
```

## Troubleshooting

- **No networks found**: Make sure WiFi is enabled on your Mac
- **Permission errors**: You may need to grant Terminal/terminal app network access in System Preferences > Security & Privacy
- **Alternative scan methods**: The tool includes sample data generation for demonstration when airport utility is unavailable

## License

This tool is provided as-is for educational and personal use.








