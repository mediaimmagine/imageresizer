#!/usr/bin/env python3
"""
Real WiFi Network Scanner for macOS
Uses CoreWLAN framework to scan for nearby WiFi networks
"""

import subprocess
import re
import json
from datetime import datetime

def scan_with_wdutil():
    """Try to scan using wdutil (requires sudo)"""
    try:
        result = subprocess.run(
            ['sudo', 'wdutil', 'dump'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        return None

def scan_with_system_profiler():
    """Scan WiFi using system_profiler"""
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType', '-xml'],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error with system_profiler: {e}")
        return None

def scan_with_networksetup():
    """Try to get WiFi info using networksetup"""
    try:
        result = subprocess.run(
            ['networksetup', '-listallhardwareports'],
            capture_output=True,
            text=True
        )
        
        wifi_port = None
        for line in result.stdout.split('\n'):
            if 'Wi-Fi' in line or 'AirPort' in line:
                # Next line should have device name
                wifi_port = line
                break
        
        if wifi_port:
            # Get current network info
            result = subprocess.run(
                ['networksetup', '-getairportnetwork', 'en0'],
                capture_output=True,
                text=True
            )
            return result.stdout
        return None
    except Exception as e:
        return None

def scan_with_airport_direct():
    """Use airport utility directly without symlink"""
    airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions!' \
                   '/Current/Resources/airport'
    
    # Try different possible paths
    paths = [
        '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
        '/usr/local/bin/airport',
        airport_path
    ]
    
    for path in paths:
        try:
            result = subprocess.run(
                [path, '-s'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and len(result.stdout) > 0:
                return result.stdout
        except Exception:
            continue
    
    return None

def parse_airport_output(output):
    """Parse airport -s output"""
    networks = []
    
    if not output or 'deprecated' in output.lower():
        return networks
    
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return networks
    
    # Parse header to understand format
    header = lines[0]
    
    for line in lines[1:]:
        if not line.strip():
            continue
        
        # Split by whitespace, but preserve SSID if it contains spaces
        parts = re.split(r'\s{2,}', line.strip())
        
        if len(parts) >= 4:
            ssid = parts[0]
            bssid = parts[1] if len(parts) > 1 else 'N/A'
            rssi = parts[2] if len(parts) > 2 else 'N/A'
            channel = parts[3] if len(parts) > 3 else 'N/A'
            security = ' '.join(parts[4:]) if len(parts) > 4 else 'Open'
            
            try:
                rssi_val = int(rssi) if rssi != 'N/A' else -100
                channel_val = int(channel) if channel != 'N/A' and channel.isdigit() else 0
            except (ValueError, AttributeError):
                continue
            
            networks.append({
                'SSID': ssid,
                'BSSID': bssid,
                'RSSI': rssi_val,
                'Channel': channel_val,
                'Security': security,
                'Quality': min(100, max(0, 2 * (rssi_val + 100)))
            })
    
    return networks

def scan_real_networks():
    """Try multiple methods to scan for real WiFi networks"""
    print("Scanning for WiFi networks...")
    print("=" * 50)
    
    # Method 1: Try airport utility
    print("\nTrying method 1: airport utility...")
    airport_output = scan_with_airport_direct()
    if airport_output:
        networks = parse_airport_output(airport_output)
        if networks:
            print(f"✓ Found {len(networks)} networks using airport utility")
            return networks
        else:
            print("  No networks parsed from airport output")
    
    # Method 2: Try system_profiler
    print("\nTrying method 2: system_profiler...")
    profiler_output = scan_with_system_profiler()
    if profiler_output:
        print("  system_profiler output received (needs parsing)")
        # Could parse XML here
    
    # Method 3: Try wdutil (requires sudo)
    print("\nTrying method 3: wdutil (may require password)...")
    wdutil_output = scan_with_wdutil()
    if wdutil_output:
        print("  wdutil output received (needs parsing)")
    
    # Method 4: Networksetup
    print("\nTrying method 4: networksetup...")
    netsetup_output = scan_with_networksetup()
    if netsetup_output:
        print(f"  Current network: {netsetup_output}")
    
    print("\n" + "=" * 50)
    return []

def display_networks(networks):
    """Display scanned networks"""
    if not networks:
        print("\n❌ No WiFi networks detected")
        print("\nPossible reasons:")
        print("  1. WiFi is disabled on your Mac")
        print("  2. No WiFi networks in range")
        print("  3. Permission issues (Terminal needs network access)")
        print("\nTo fix permissions:")
        print("  - Go to System Preferences > Security & Privacy > Privacy")
        print("  - Select 'Network' and ensure Terminal has access")
        return
    
    # Sort by signal strength
    networks.sort(key=lambda x: x['RSSI'], reverse=True)
    
    print(f"\n✓ Found {len(networks)} WiFi networks")
    print("\n" + "=" * 80)
    print(f"{'SSID':<30} {'Signal (dBm)':<15} {'Quality':<15} {'Channel':<10}")
    print("=" * 80)
    
    for i, net in enumerate(networks, 1):
        ssid = net['SSID'][:28]
        rssi = net['RSSI']
        
        # Create quality bar
        if rssi > -67:
            quality = "●●●●● Excellent"
        elif rssi > -70:
            quality = "●●●●○ Good"
        elif rssi > -80:
            quality = "●●●○○ Fair"
        elif rssi > -90:
            quality = "●●○○○ Weak"
        else:
            quality = "●○○○○ Very Weak"
        
        print(f"{ssid:<30} {rssi:<15} {quality:<15} {net['Channel']:<10}")
        
        if i == 10:  # Limit display to top 10
            if len(networks) > 10:
                print(f"\n... and {len(networks) - 10} more networks")
            break
    
    print("=" * 80)
    
    # Show statistics
    print("\nStatistics:")
    print(f"  Total networks: {len(networks)}")
    print(f"  Strongest signal: {networks[0]['SSID']} ({networks[0]['RSSI']} dBm)")
    print(f"  Average signal: {sum(n['RSSI'] for n in networks) / len(networks):.1f} dBm")
    
    # Channel distribution
    channels = {}
    for net in networks:
        ch = net['Channel']
        if ch > 0:
            channels[ch] = channels.get(ch, 0) + 1
    
    if channels:
        most_used = max(channels, key=channels.get)
        print(f"  Most used channel: {most_used} ({channels[most_used]} networks)")

def save_network_json(networks, filename='wifi_networks.json'):
    """Save networks to JSON file"""
    data = {
        'scan_time': datetime.now().isoformat(),
        'total_networks': len(networks),
        'networks': networks
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Network data saved to: {filename}")

def main():
    print("\n" + "=" * 60)
    print("WiFi Real Network Scanner for macOS")
    print("=" * 60)
    
    networks = scan_real_networks()
    display_networks(networks)
    
    if networks:
        save_network_json(networks)
        
        # Ask if user wants to create visualization
        print("\n" + "=" * 60)
        print("To create a visual coverage diagram, run:")
        print("  python3 wifi_coverage_scanner.py")
        print("=" * 60)
    
    print()  # Extra newline

if __name__ == '__main__':
    main()








