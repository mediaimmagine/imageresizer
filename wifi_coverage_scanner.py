#!/usr/bin/env python3
"""
WiFi Coverage Scanner and Visualizer
Scans nearby WiFi networks and displays coverage diagrams
"""

import subprocess
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
import numpy as np
import time
import os
import sys

class WiFiScanner:
    def __init__(self):
        self.networks = []
        self.check_airport_utility()
    
    def check_airport_utility(self):
        """Check if airport utility is available"""
        airport_paths = [
            '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
            '/usr/local/bin/airport'
        ]
        
        self.airport_path = None
        for path in airport_paths:
            if os.path.exists(path):
                self.airport_path = path
                break
        
        if not self.airport_path:
            print("Warning: airport utility not found. Trying networksetup alternative.")
    
    def scan_networks(self):
        """Scan for WiFi networks"""
        networks = []
        
        try:
            if self.airport_path:
                # Use airport utility
                result = subprocess.run(
                    [self.airport_path, '-s'],
                    capture_output=True,
                    text=True
                )
                
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            ssid = parts[0]
                            bssid = parts[1]
                            rssi = parts[2]
                            channel = parts[3]
                            security = ' '.join(parts[6:]) if len(parts) > 6 else ''
                            
                            try:
                                rssi_val = int(rssi)
                                channel_val = int(channel) if channel != 'N/A' else 0
                                
                                networks.append({
                                    'SSID': ssid,
                                    'BSSID': bssid,
                                    'RSSI': rssi_val,
                                    'Channel': channel_val,
                                    'Security': security,
                                    'Quality': min(100, max(0, 2 * (rssi_val + 100)))
                                })
                            except ValueError:
                                continue
            else:
                # Alternative: Use networksetup (less detailed)
                print("Using networksetup as fallback (limited info)")
                result = subprocess.run(
                    ['networksetup', '-listallhardwareports'],
                    capture_output=True,
                    text=True
                )
                # This is limited, so we'll create a mock example
                networks = self.get_sample_networks()
        
        except Exception as e:
            print(f"Error scanning networks: {e}")
            print("Generating sample data for demonstration...")
            networks = self.get_sample_networks()
        
        self.networks = networks
        return networks
    
    def get_sample_networks(self):
        """Generate sample network data for demonstration"""
        import random
        ssids = ['HomeNetwork', 'Neighbor_WiFi', 'Corporate-Guest', 'Cafe-WiFi', 
                 'iPhone_John', 'MyNetwork_5G', 'Office_WiFi', 'Linksys_Router']
        
        channels = [1, 6, 11, 36, 40, 44, 149, 153, 157, 161]
        
        networks = []
        for i, ssid in enumerate(ssids):
            networks.append({
                'SSID': ssid,
                'BSSID': f"00:{(i+1):02d}:ab:cd:ef:{i:02x}",
                'RSSI': random.randint(-90, -30),
                'Channel': random.choice(channels),
                'Security': 'WPA2' if random.random() > 0.2 else 'Open',
                'Quality': random.randint(20, 100)
            })
        
        return networks
    
    def visualize_coverage(self, save_path='wifi_coverage.png'):
        """Create a visual coverage diagram"""
        if not self.networks:
            print("No networks to visualize")
            return
        
        # Sort by signal strength
        sorted_networks = sorted(self.networks, key=lambda x: x['RSSI'], reverse=True)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        
        # 1. Signal Strength Bar Chart
        ax1 = plt.subplot(2, 2, 1)
        ssids = [net['SSID'][:15] for net in sorted_networks]
        rssis = [net['RSSI'] for net in sorted_networks]
        colors = plt.cm.RdYlGn(1 - (np.array(rssis) - min(rssis)) / (max(rssis) - min(rssis) + 1))
        
        bars = ax1.barh(range(len(ssids)), rssis, color=colors)
        ax1.set_yticks(range(len(ssids)))
        ax1.set_yticklabels(ssids)
        ax1.set_xlabel('Signal Strength (dBm)')
        ax1.set_title('WiFi Networks by Signal Strength')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(x=-67, color='green', linestyle='--', alpha=0.5, label='Excellent (-67 dBm)')
        ax1.axvline(x=-70, color='yellow', linestyle='--', alpha=0.5, label='Good (-70 dBm)')
        ax1.axvline(x=-80, color='orange', linestyle='--', alpha=0.5, label='Fair (-80 dBm)')
        ax1.axvline(x=-90, color='red', linestyle='--', alpha=0.5, label='Weak (-90 dBm)')
        ax1.legend(loc='lower right')
        
        # Add value labels
        for i, (bar, rssi) in enumerate(zip(bars, rssis)):
            ax1.text(rssi, i, f' {rssi} dBm', va='center', fontsize=8)
        
        # 2. Channel Distribution
        ax2 = plt.subplot(2, 2, 2)
        channels = [net['Channel'] for net in sorted_networks]
        channel_counts = {}
        for ch in channels:
            channel_counts[ch] = channel_counts.get(ch, 0) + 1
        
        if channel_counts:
            ch_keys = sorted(channel_counts.keys())
            ch_values = [channel_counts[ch] for ch in ch_keys]
            bars = ax2.bar(ch_keys, ch_values, color='steelblue')
            ax2.set_xlabel('Channel')
            ax2.set_ylabel('Number of Networks')
            ax2.set_title('Network Distribution by Channel')
            ax2.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, val in zip(bars, ch_values):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f'{val}', ha='center', va='bottom', fontsize=9)
        
        # 3. Coverage Map (simulated)
        ax3 = plt.subplot(2, 2, 3)
        self.create_coverage_map(ax3, sorted_networks)
        
        # 4. Network Details Table
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        self.create_details_table(ax4, sorted_networks)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Coverage diagram saved to: {save_path}")
        return save_path
    
    def create_coverage_map(self, ax, networks):
        """Create a simulated coverage map showing signal strength"""
        # Simulate position in 2D space
        n = len(networks)
        positions = self.get_simulated_positions(n)
        
        # Normalize signal strength for display
        min_rssi = min(net['RSSI'] for net in networks)
        max_rssi = max(net['RSSI'] for net in networks)
        
        for i, net in enumerate(networks):
            x, y = positions[i]
            rssi = net['RSSI']
            
            # Map RSSI to radius (stronger signal = larger coverage circle)
            radius = 30 + (rssi - min_rssi) / (max_rssi - min_rssi + 1) * 20
            
            # Map RSSI to color
            normalized = (rssi - min_rssi) / (max_rssi - min_rssi + 1)
            color = plt.cm.RdYlGn(1 - normalized)
            alpha = 0.3
            
            # Draw coverage circle
            circle = Circle((x, y), radius, facecolor=color, alpha=alpha, edgecolor='black', linewidth=1)
            ax.add_patch(circle)
            
            # Draw network point
            ax.plot(x, y, 'o', color='black', markersize=8)
            
            # Label network
            ax.annotate(net['SSID'][:10], (x, y), xytext=(5, 5), 
                       textcoords='offset points', fontsize=7, fontweight='bold')
        
        ax.set_xlim(-50, 50)
        ax.set_ylim(-50, 50)
        ax.set_aspect('equal')
        ax.set_title('Simulated WiFi Coverage Map')
        ax.set_xlabel('Distance (units)')
        ax.set_ylabel('Distance (units)')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        rssi_ranges = [(-30, 'Excellent'), (-70, 'Good'), (-80, 'Fair'), (-90, 'Weak')]
        patches = []
        for rssi_val, label in rssi_ranges:
            patches.append(mpatches.Patch(color=plt.cm.RdYlGn(1 - (rssi_val - min_rssi) / (max_rssi - min_rssi + 1)), 
                                         label=f'{label} ({rssi_val} dBm)', alpha=0.7))
        ax.legend(handles=patches, loc='upper right', fontsize=7)
    
    def get_simulated_positions(self, n):
        """Generate simulated positions for networks"""
        np.random.seed(42)  # For consistent positioning
        positions = []
        
        # Distribute networks in a circle with some randomness
        angles = np.linspace(0, 2*np.pi, n, endpoint=False)
        
        for i, angle in enumerate(angles):
            radius = 15 + np.random.uniform(-5, 5)
            x = radius * np.cos(angle) + np.random.uniform(-3, 3)
            y = radius * np.sin(angle) + np.random.uniform(-3, 3)
            positions.append((x, y))
        
        return positions
    
    def create_details_table(self, ax, networks):
        """Create a detailed table of network information"""
        # Truncate to top 10 networks
        display_networks = networks[:10]
        
        table_data = []
        for net in display_networks:
            signal_quality = "●●●●●" if net['RSSI'] > -67 else \
                            "●●●●○" if net['RSSI'] > -70 else \
                            "●●●○○" if net['RSSI'] > -80 else \
                            "●●○○○" if net['RSSI'] > -90 else "●○○○○"
            
            table_data.append([
                net['SSID'][:15],
                f"{net['RSSI']} dBm",
                str(net['Channel']),
                signal_quality
            ])
        
        table = ax.table(cellText=table_data,
                        colLabels=['SSID', 'Signal', 'Channel', 'Quality'],
                        cellLoc='left',
                        loc='upper left',
                        colWidths=[0.35, 0.2, 0.15, 0.3])
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.0, 1.5)
        
        # Style header row
        for i in range(4):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color code signal strength rows
        for i in range(len(table_data)):
            for j in range(4):
                table[(i+1, j)].set_facecolor('#F2F2F2')
        
        ax.set_title('Network Details (Top 10)', fontsize=10, fontweight='bold', pad=20)
    
    def scan_and_visualize(self, continuous=False, interval=5):
        """Scan networks and create visualization"""
        if continuous:
            print("Starting continuous scanning mode (Ctrl+C to stop)...")
            scan_count = 0
            try:
                while True:
                    scan_count += 1
                    print(f"\nScan #{scan_count} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    networks = self.scan_networks()
                    print(f"Found {len(networks)} networks")
                    
                    if networks:
                        self.networks = networks
                        save_path = f'wifi_coverage_{scan_count:03d}.png'
                        self.visualize_coverage(save_path)
                    else:
                        print("No networks found, skipping visualization")
                    
                    # Wait before next scan
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\nScanning stopped by user")
        else:
            networks = self.scan_networks()
            
            if not networks:
                print("\nNo WiFi networks detected.")
                print("\nThis could be because:")
                print("1. WiFi is disabled on your Mac")
                print("2. Airport utility is not accessible")
                print("3. No networks in range")
                print("\nGenerating sample data for demonstration...")
                networks = self.get_sample_networks()
            
            # Update self.networks for visualization
            self.networks = networks
            
            print(f"\nFound {len(networks)} WiFi networks")
            
            # Display summary
            print("\nTop 5 Networks by Signal Strength:")
            for i, net in enumerate(sorted(networks, key=lambda x: x['RSSI'], reverse=True)[:5], 1):
                print(f"{i}. {net['SSID']}: {net['RSSI']} dBm (Channel {net['Channel']})")
            
            save_path = self.visualize_coverage()
            if save_path:
                print(f"\nCoverage diagram saved to: {save_path}")
                
                # Try to open the image
                try:
                    subprocess.run(['open', save_path], check=False)
                except:
                    print(f"Open the file manually: {save_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scan WiFi networks and visualize coverage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wifi_coverage_scanner.py                    # Single scan
  python wifi_coverage_scanner.py --continuous       # Continuous scanning
  python wifi_coverage_scanner.py -c -i 10           # Scan every 10 seconds
        """
    )
    
    parser.add_argument('-c', '--continuous', action='store_true',
                       help='Continuous scanning mode')
    parser.add_argument('-i', '--interval', type=int, default=5,
                       help='Interval between scans in seconds (default: 5)')
    
    args = parser.parse_args()
    
    scanner = WiFiScanner()
    scanner.scan_and_visualize(continuous=args.continuous, interval=args.interval)


if __name__ == '__main__':
    main()

