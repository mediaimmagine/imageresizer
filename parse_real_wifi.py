#!/usr/bin/env python3
"""
Parse real WiFi networks from system_profiler output
"""

import subprocess
import re
import json
from datetime import datetime

def parse_system_profiler():
    """Parse system_profiler output to extract WiFi networks"""
    networks = []
    
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        
        # Find the "Other Local Wi-Fi Networks:" section
        in_networks_section = False
        current_ssid = None
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'Other Local Wi-Fi Networks:' in line:
                in_networks_section = True
                continue
            
            if in_networks_section:
                # Check if this is a new SSID (no indentation)
                if line and not line.startswith(' ') and ':' in line:
                    if current_ssid and current_network:
                        # Save previous network
                        # Estimate RSSI if not provided (based on connecting status)
                        if 'Signal / Noise' not in current_network.get('raw_data', ''):
                            # Estimate based on typical values for visible but not connected networks
                            current_network['RSSI'] = -70
                        networks.append(current_network)
                    
                    # Start new network
                    current_ssid = line.rstrip(':')
                    current_network = {
                        'SSID': current_ssid,
                        'Channel': 0,
                        'Security': 'Unknown',
                        'Band': 'Unknown',
                        'raw_data': line
                    }
                
                # Parse network properties
                if current_ssid:
                    if 'PHY Mode:' in line:
                        current_network['raw_data'] += '\n' + line
                        # Determine band from PHY mode
                        if '802.11a' in line or '5GHz' in line:
                            current_network['Band'] = '5GHz'
                        elif '802.11b/g/n' in line or '2GHz' in line:
                            current_network['Band'] = '2.4GHz'
                    
                    if 'Channel:' in line:
                        current_network['raw_data'] += '\n' + line
                        match = re.search(r'(\d+)', line)
                        if match:
                            current_network['Channel'] = int(match.group(1))
                    
                    if 'Security:' in line:
                        current_network['raw_data'] += '\n' + line
                        sec = line.split(':', 1)[1].strip()
                        if 'WPA2' in sec:
                            current_network['Security'] = 'WPA2'
                        elif 'WPA3' in sec:
                            current_network['Security'] = 'WPA2/WPA3'
                        elif sec == 'None':
                            current_network['Security'] = 'Open'
                        else:
                            current_network['Security'] = sec
                    
                    if 'Signal / Noise:' in line:
                        current_network['raw_data'] += '\n' + line
                        match = re.search(r'(-?\d+)\s*dBm', line)
                        if match:
                            current_network['RSSI'] = int(match.group(1))
        
        # Add the last network
        if current_ssid and current_network:
            if 'RSSI' not in current_network:
                current_network['RSSI'] = -70
            networks.append(current_network)
        
        return networks
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def display_networks(networks):
    """Display the networks"""
    # Group by SSID to handle multiple bands
    unique_networks = {}
    for net in networks:
        ssid = net['SSID']
        if ssid not in unique_networks:
            unique_networks[ssid] = []
        unique_networks[ssid].append(net)
    
    # Sort by signal strength
    all_with_rssi = []
    for ssid, variants in unique_networks.items():
        # Get the strongest signal from any variant
        best_rssi = min(n['RSSI'] for n in variants)
        best_net = next(n for n in variants if n['RSSI'] == best_rssi)
        best_net['band_count'] = len(variants)
        best_net['bands'] = [v['Band'] for v in variants]
        all_with_rssi.append(best_net)
    
    all_with_rssi.sort(key=lambda x: x['RSSI'])
    
    print("\n" + "=" * 80)
    print(f"{'SSID':<25} {'Signal (dBm)':<15} {'Bands':<15} {'Channel':<10} {'Security':<15}")
    print("=" * 80)
    
    for net in all_with_rssi:
        ssid = net['SSID'][:23]
        rssi = net['RSSI']
        bands = ','.join(set(net['bands']))[:13]
        channel = str(net['Channel']) + ' (best)'
        security = net['Security'][:13]
        
        print(f"{ssid:<25} {rssi:<15} {bands:<15} {channel:<10} {security:<15}")
    
    print("=" * 80)
    print(f"\nTotal unique SSIDs: {len(all_with_rssi)}")
    
    return all_with_rssi

def save_to_json(networks, filename='wifi_real_networks.json'):
    """Save networks to JSON"""
    data = {
        'scan_time': datetime.now().isoformat(),
        'total_unique_networks': len(networks),
        'networks': networks
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Data saved to: {filename}")

def main():
    print("Scanning for real WiFi networks...")
    print("=" * 80)
    
    networks = parse_system_profiler()
    
    if networks:
        print(f"Found {len(networks)} network entries")
        unique_networks = display_networks(networks)
        save_to_json(networks)
        
        print("\n" + "=" * 80)
        print("To create a visual coverage diagram, run:")
        print("  python3 wifi_coverage_scanner.py")
        print("=" * 80)
    else:
        print("\nNo networks found. Make sure WiFi is enabled and try again.")

if __name__ == '__main__':
    main()




