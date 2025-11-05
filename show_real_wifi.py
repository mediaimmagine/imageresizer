#!/usr/bin/env python3
"""Show real WiFi networks from system_profiler output"""

import subprocess
import re

def get_wifi_networks():
    """Extract WiFi networks from system_profiler"""
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        
        # Find networks section
        networks_section = False
        networks = {}
        
        for line in output.split('\n'):
            stripped = line.strip()
            
            if 'Other Local Wi-Fi Networks:' in line:
                networks_section = True
                continue
            
            if networks_section and stripped and not stripped.startswith(' '):
                # Check if this is a network SSID (line ends with colon)
                if stripped.endswith(':'):
                    ssid = stripped[:-1].strip()
                    if ssid not in networks:
                        networks[ssid] = {'SSID': ssid, 'bands': [], 'best_rssi': 100}
            
            elif networks_section and 'Signal / Noise:' in line:
                # Extract RSSI
                match = re.search(r'(-?\d+)\s*dBm', line)
                if match:
                    rssi = int(match.group(1))
                    # Find the most recent SSID
                    current_ssid = None
                    i = output.split('\n').index(line)
                    for j in range(i-5, i+1):
                        prev_line = output.split('\n')[j] if j >= 0 else ''
                        if prev_line.strip().endswith(':') and prev_line.strip()[0] != ' ':
                            current_ssid = prev_line.strip()[:-1]
                    if current_ssid and current_ssid in networks:
                        if networks[current_ssid]['best_rssi'] > rssi:
                            networks[current_ssid]['best_rssi'] = rssi
        
        return list(networks.values())
        
    except Exception as e:
        return []

# Get networks
print("\n" + "=" * 70)
print("Real WiFi Networks Detected")
print("=" * 70)

networks = get_wifi_networks()

if networks:
    # Show connected network first
    print("\n📡 Currently Connected:")
    subprocess.run(['networksetup', '-getairportnetwork', 'en0'], text=True)
    
    print("\n📊 Nearby WiFi Networks:")
    print("=" * 70)
    
    # Sort by SSID
    networks.sort(key=lambda x: x['SSID'])
    
    for net in networks:
        ssid = net['SSID']
        rssi = net['best_rssi'] if net['best_rssi'] != 100 else -70
        quality = ""
        
        if rssi >= -50:
            quality = "●●●●● Excellent"
        elif rssi >= -67:
            quality = "●●●●○ Good"
        elif rssi >= -70:
            quality = "●●●○○ Fair"
        elif rssi >= -80:
            quality = "●●○○○ Weak"
        else:
            quality = "●○○○○ Very Weak"
        
        print(f"{ssid:<40} {quality}")
    
    print("=" * 70)
    print(f"\nTotal unique SSIDs found: {len(networks)}")
else:
    print("No networks detected")

print()








