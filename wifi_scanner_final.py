#!/usr/bin/env python3
"""
WiFi Network Scanner - Final Version
Uses system_profiler to extract WiFi network information
"""

import subprocess
import re
import json
from datetime import datetime

def parse_system_profiler_wifi():
    """Parse system_profiler SPAirPortDataType output"""
    networks = []
    
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        
        if not output:
            return networks
        
        # Look for network sections
        lines = output.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for SSID
            if 'SSID_STR:' in line or 'SSID STR:' in line:
                ssid = re.search(r':\s*(.+)$', line)
                if ssid:
                    ssid_name = ssid.group(1).strip()
                    
                    # Look ahead for additional info
                    network_info = {'SSID': ssid_name}
                    
                    # Check next few lines for more info
                    for j in range(i, min(i + 20, len(lines))):
                        next_line = lines[j].strip()
                        
                        if 'PHY_MODE:' in next_line or 'PHY Mode:' in next_line:
                            network_info['PHY Mode'] = re.search(r':\s*(.+)$', next_line).group(1) if re.search(r':\s*(.+)$', next_line) else 'Unknown'
                        
                        if 'BSSID:' in next_line:
                            network_info['BSSID'] = re.search(r':\s*(.+)$', next_line).group(1) if re.search(r':\s*(.+)$', next_line) else 'Unknown'
                        
                        if 'CHANNEL:' in next_line or 'Channel:' in next_line:
                            channel_match = re.search(r':\s*(\d+)', next_line)
                            if channel_match:
                                network_info['Channel'] = int(channel_match.group(1))
                        
                        if 'AUTH_WPA_PSK' in next_line or 'WPA/WPA2' in next_line:
                            network_info['Security'] = 'WPA/WPA2'
                        elif 'AUTH_OPEN' in next_line:
                            network_info['Security'] = 'Open'
                        
                        if 'RSSI:' in next_line:
                            rssi_match = re.search(r':\s*(-?\d+)', next_line)
                            if rssi_match:
                                network_info['RSSI'] = int(rssi_match.group(1))
                    else:
                        # Default values if not found
                        network_info.setdefault('Channel', 0)
                        network_info.setdefault('Security', 'Unknown')
                        network_info.setdefault('RSSI', -85)
                    
                    networks.append(network_info)
            
            i += 1
        
        return networks
        
    except Exception as e:
        print(f"Error parsing system_profiler: {e}")
        return []

def get_airport_raw():
    """Get raw airport output with better parsing"""
    airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
    
    try:
        result = subprocess.run(
            [airport_path, '-s'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return result.stdout
        
    except Exception as e:
        print(f"Airport error: {e}")
        return None

def parse_airport_improved(output):
    """Improved airport output parsing"""
    networks = []
    
    if not output:
        return networks
    
    # Check if it's just a warning
    lines = output.split('\n')
    non_warning_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip warning lines
        if 'WARNING' not in line and 'deprecated' not in line.lower() and \
           'diagnosing' not in line.lower() and 'wdutil' not in line.lower() and \
           'future release' not in line.lower() and line:
            non_warning_lines.append(line)
    
    if not non_warning_lines:
        return networks
    
    # Try to parse the remaining lines
    for line in non_warning_lines:
        # Remove extra spaces and split on multiple spaces
        parts = re.split(r'\s{2,}', line)
        
        if len(parts) >= 3:
            ssid = parts[0]
            bssid = parts[1] if len(parts) > 1 else 'N/A'
            
            # Try to find RSSI (usually negative number)
            rssi = -85  # default
            channel = 0
            
            for part in parts[2:]:
                if re.match(r'^-\d+$', part):
                    rssi = int(part)
                elif part.isdigit():
                    channel = int(part)
            
            networks.append({
                'SSID': ssid,
                'BSSID': bssid,
                'RSSI': rssi,
                'Channel': channel,
                'Security': 'Unknown',
                'Quality': min(100, max(0, 2 * (rssi + 100)))
            })
    
    return networks

def scan_networks():
    """Main scanning function"""
    print("\n" + "=" * 70)
    print("WiFi Network Scanner")
    print("=" * 70)
    
    all_networks = {}
    
    # Try airport first (usually most complete)
    print("\n1. Scanning with airport utility...")
    airport_output = get_airport_raw()
    if airport_output:
        print(f"   Raw output length: {len(airport_output)} characters")
        networks = parse_airport_improved(airport_output)
        print(f"   Parsed {len(networks)} networks")
        
        # Add to all_networks dictionary
        for net in networks:
            all_networks[net['SSID']] = net
    
    # Try system_profiler as backup
    print("\n2. Scanning with system_profiler...")
    profiler_networks = parse_system_profiler_wifi()
    print(f"   Found {len(profiler_networks)} networks")
    
    # Merge results
    for net in profiler_networks:
        ssid = net.get('SSID', 'Unknown')
        if ssid not in all_networks:
            all_networks[ssid] = net
        else:
            # Merge info from both sources
            existing = all_networks[ssid]
            for key, value in net.items():
                if key not in existing or existing[key] in ['Unknown', 0, -85]:
                    existing[key] = value
    
    # Convert to list
    networks = list(all_networks.values())
    
    return networks

def display_results(networks):
    """Display scan results"""
    if not networks:
        print("\n❌ No WiFi networks detected")
        print("\nTroubleshooting:")
        print("1. Make sure WiFi is turned ON")
        print("2. Check if you're near any WiFi networks")
        print("3. Grant Terminal network access:")
        print("   System Preferences > Security & Privacy > Privacy > Network")
        return
    
    # Sort by signal strength if available
    networks.sort(key=lambda x: x.get('RSSI', -100), reverse=True)
    
    print(f"\n✓ Found {len(networks)} WiFi networks")
    print("\n" + "=" * 70)
    print(f"{'SSID':<25} {'Signal':<12} {'Quality':<15} {'Channel':<10}")
    print("=" * 70)
    
    for net in networks:
        ssid = net.get('SSID', 'Unknown')[:23]
        rssi = net.get('RSSI', -85)
        
        # Quality visualization
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
        
        print(f"{ssid:<25} {rssi:<12} {quality:<15} {net.get('Channel', 'N/A'):<10}")
    
    print("=" * 70)

def save_results(networks):
    """Save results to JSON"""
    data = {
        'scan_time': datetime.now().isoformat(),
        'total_networks': len(networks),
        'networks': networks
    }
    
    filename = 'wifi_real_networks.json'
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Results saved to: {filename}")

def main():
    networks = scan_networks()
    display_results(networks)
    
    if networks:
        save_results(networks)
        print("\nTo create a visual coverage diagram:")
        print("  python3 wifi_coverage_scanner.py")
    
    print()

if __name__ == '__main__':
    main()






