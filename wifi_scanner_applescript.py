#!/usr/bin/env python3
"""
WiFi Network Scanner using AppleScript
Works on modern macOS where airport utility is deprecated
"""

import subprocess
import json
from datetime import datetime

def run_applescript(script):
    """Run AppleScript and return output"""
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return None

def scan_with_applescript():
    """Scan WiFi networks using AppleScript"""
    script = '''
    set networkList to {}
    try
        set wifiInfo to do shell script "networksetup -listpreferredwirelessnetworks en0"
        repeat with networkItem in paragraphs of wifiInfo
            if networkItem is not "" then
                set networkList to networkList & {networkItem}
            end if
        end repeat
    end try
    
    set output to ""
    repeat with net in networkList
        set output to output & net & "\\n"
    end repeat
    return output
    '''
    
    result = run_applescript(script)
    if result:
        networks = []
        for line in result.split('\n'):
            line = line.strip()
            if line and not line.startswith('Preferred'):
                networks.append(line)
        return networks
    return []

def get_wifi_status():
    """Check if WiFi is enabled"""
    script = '''
    do shell script "networksetup -getairportpower en0"
    '''
    result = run_applescript(script)
    return result

def get_current_wifi():
    """Get current WiFi network"""
    script = '''
    try
        do shell script "networksetup -getairportnetwork en0"
    on error
        return "Not connected"
    end try
    '''
    result = run_applescript(script)
    return result

def try_airport_with_stderr():
    """Try airport and capture stderr too"""
    airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
    
    try:
        result = subprocess.run(
            [airport_path, '-s'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Print both stdout and stderr for debugging
        if result.stderr:
            print(f"stderr: {result.stderr}")
        if result.stdout:
            print(f"stdout length: {len(result.stdout)}")
            
        return result.stdout
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def use_python_wifi_module():
    """Try using Python WiFi module if available"""
    try:
        import wifi
        cells = wifi.Cell.all('en0')
        networks = []
        for cell in cells:
            networks.append({
                'SSID': cell.ssid,
                'RSSI': 'N/A',
                'Channel': cell.channel if hasattr(cell, 'channel') else 'N/A',
                'Security': cell.encryption_type if hasattr(cell, 'encryption_type') else 'Unknown'
            })
        return networks
    except ImportError:
        return None
    except Exception as e:
        print(f"WiFi module error: {e}")
        return None

def scan_comprehensive():
    """Try all available methods to scan networks"""
    print("\nScanning for WiFi networks using multiple methods...")
    print("=" * 70)
    
    # Check WiFi status first
    print("\n1. Checking WiFi status...")
    wifi_status = get_wifi_status()
    current_wifi = get_current_wifi()
    print(f"   WiFi Status: {wifi_status}")
    print(f"   Current Network: {current_wifi}")
    
    # Try airport with debug info
    print("\n2. Trying airport utility (with debug)...")
    airport_output = try_airport_with_stderr()
    
    # If we got output, try to parse it even if it looks like it has just the warning
    if airport_output:
        lines = airport_output.split('\n')
        actual_networks = [l for l in lines if l.strip() and 'WARNING' not in l and 'deprecated' not in l.lower() and 'diagnosing' not in l.lower() and 'wdutil' not in l.lower()]
        
        if len(actual_networks) > 0:
            print(f"   Found {len(actual_networks)} potential network lines")
            # Print first few to see format
            for line in actual_networks[:3]:
                print(f"   Line: {line[:80]}")
        else:
            print("   No network data in airport output")
    
    # Try system_profiler
    print("\n3. Trying system_profiler...")
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout:
            lines = result.stdout.split('\n')
            wifi_lines = [l for l in lines if 'WiFi' in l or 'Network' in l or 'SSID' in l]
            if wifi_lines:
                print(f"   Found {len(wifi_lines)} relevant lines")
                for line in wifi_lines[:5]:
                    print(f"   {line[:80]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Try Python WiFi module
    print("\n4. Trying Python WiFi module...")
    networks_py = use_python_wifi_module()
    if networks_py:
        print(f"   ✓ Found {len(networks_py)} networks using Python WiFi module")
        return networks_py
    else:
        print("   Python WiFi module not available")
    
    # Try to install Python WiFi module
    print("\n5. Attempting to install WiFi module...")
    try:
        subprocess.run(['pip3', 'install', 'wifi'], check=False, 
                      capture_output=True, timeout=30)
        networks_py = use_python_wifi_module()
        if networks_py:
            print(f"   ✓ Found {len(networks_py)} networks after installing WiFi module")
            return networks_py
    except Exception as e:
        print(f"   Could not install: {e}")
    
    print("\n" + "=" * 70)
    return []

def display_results(networks):
    """Display the scan results"""
    if not networks:
        print("\n❌ Could not detect any WiFi networks")
        print("\nTroubleshooting steps:")
        print("1. Ensure WiFi is enabled: Turn WiFi on in system menu")
        print("2. Check network permissions:")
        print("   System Preferences > Security & Privacy > Privacy > Network")
        print("   Make sure Terminal has network access")
        print("3. Try running Wireless Diagnostics:")
        print("   Hold Option key > Click WiFi icon > Open Wireless Diagnostics")
        print("4. Modern macOS has restricted airport utility access")
        return
    
    print(f"\n✓ Detected {len(networks)} WiFi networks")
    print("\n" + "=" * 70)
    print(f"{'SSID':<30} {'Channel':<15} {'Security':<20}")
    print("=" * 70)
    
    for net in networks[:20]:  # Show first 20
        ssid = net.get('SSID', 'Unknown')[:28]
        channel = str(net.get('Channel', 'N/A'))
        security = net.get('Security', 'Unknown')[:18]
        print(f"{ssid:<30} {channel:<15} {security:<20}")
    
    if len(networks) > 20:
        print(f"\n... and {len(networks) - 20} more networks")
    
    print("=" * 70)

def main():
    print("\n" + "=" * 70)
    print("WiFi Network Scanner for macOS (Comprehensive)")
    print("=" * 70)
    
    networks = scan_comprehensive()
    display_results(networks)
    
    # Save to JSON
    if networks:
        data = {
            'scan_time': datetime.now().isoformat(),
            'total_networks': len(networks),
            'networks': networks
        }
        
        with open('wifi_real_networks.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Data saved to: wifi_real_networks.json")
        print("\nRun 'python3 wifi_coverage_scanner.py' to create visualization")
    
    print()

if __name__ == '__main__':
    main()






