#!/usr/bin/env python3
"""
Correctly parse WiFi networks from system_profiler
"""

import subprocess
import re
import json
from datetime import datetime

def parse_wifi_networks():
    """Parse WiFi networks correctly from system_profiler"""
    networks = []
    unique_networks = {}
    
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        lines = output.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for SSIDs (lines that start with a name followed by colon in the networks section)
            if line and not line.startswith(' ') and 'Other Local Wi-Fi Networks:' in output[:i]:
                # Check if this might be a network SSID
                if ':' not in line or any(x in line for x in ['PHY Mode', 'Channel', 'Security', 'Network Type', 'Signal']):
                    i += 1
                    continue
                
                # This is likely an SSID
                ssid = line.rstrip(':')
                
                # Now gather properties for this network
                network_info = {'SSID': ssid, 'variants': []}
                
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith(' ') and ':' in next_line and 'PHY Mode' not in next_line:
                        # Hit next network
                        break
                    
                    # Parse properties
                    if 'PHY Mode:' in next_line:
                        if '5GHz' in next_line or '802.11a' in next_line:
                            network_info['variants'].append({'band': '5GHz'})
                        else:
                            network_info['variants'].append({'band': '2.4GHz'})
                    
                    if 'Channel:' in next_line:
                        match = re.search(r'(\d+)\s*\(' in next_line)
                        if match:
                            channel = int(match.group(1))
                            if network_info['variants']:
                                network_info['variants'][-1]['channel'] = channel
                            else:
                                network_info['variants'].append({'channel': channel})
                    
                    if 'Security:' in next_line:
                        sec = next_line.split(':', 1)[1].strip()
                        if network_info['variants']:
                            network_info['variants'][-1]['security'] = sec
                        else:
                            network_info['variants'].append({'security': sec})
                    
                    if 'Signal / Noise:' in next_line:
                        match = re.search(r'(-?\d+)\s*dBm', next_line)
                        if match:
                            rssi = int(match.group(1))
                            network_info['RSSI'] = rssi
                    
                    j += 1
                
                i = j
                
                # Store network
                if ssid not in unique_networks:
                    unique_networks[ssid] = network_info
                elif network_info.get('RSSI'):
                    # Update with better signal info if available
                    unique_networks[ssid]['RSSI'] = network_info['RSSI']
            else:
                i += 1
        
        # Convert to simple format
        for ssid, info in unique_networks.items():
            if info.get('RSSI'):
                networks.append({
                    'SSID': ssid,
                    'RSSI': info['RSSI'],
                    'Channel': info['variants'][0].get('channel', 0) if info['variants'] else 0,
                    'Band': info['variants'][0].get('band', 'Unknown') if info['variants'] else 'Unknown',
                    'Security': info['variants'][0].get('security', 'Unknown') if info['variants'] else 'Unknown'
                })
        
        return networks
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("Scanning real WiFi networks...")
    print("=" * 70)
    
    networks = parse_wifi_networks()
    
    if networks:
        # Sort by RSSI (best signal first)
        networks.sort(key=lambda x: x['RSSI'] if 'RSSI' in x else 100)
        
        print(f"\n✓ Found {len(networks)} WiFi networks\n")
        print("=" * 70)
        print(f"{'SSID':<30} {'Signal (dBm)':<15} {'Band':<10} {'Security'}")
        print("=" * 70)
        
        for net in networks:
            ssid = net['SSID'][:28]
            rssi = net['RSSI']
            band = net['Band'][:8]
            security = net['Security'][:20]
            
            print(f"{ssid:<30} {rssi:<15} {band:<10} {security}")
        
        print("=" * 70)
        
        # Save to JSON
        data = {
            'scan_time': datetime.now().isoformat(),
            'total_networks': len(networks),
            'networks': networks
        }
        
        with open('wifi_real_scan.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Data saved to: wifi_real_scan.json")
    else:
        print("\nNo networks detected")

if __name__ == '__main__':
    main()




