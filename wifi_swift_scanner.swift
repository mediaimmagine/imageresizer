#!/usr/bin/env swift
// WiFi Scanner using Swift and CoreWLAN framework

import Foundation
import CoreWLAN

func scanWiFiNetworks() {
    do {
        if let wifiInterface = CWWiFiClient.shared().interface() {
            print("WiFi Interface: \(wifiInterface.interfaceName ?? "Unknown")")
            print("Scanning for networks...")
            print("============================================================")
            print()
            
            let networks = try wifiInterface.scanForNetworks(withName: nil)
            
            print("Found \(networks?.count ?? 0) networks")
            print()
            print(String(format: "%-25s %-12s %-15s %-10s", "SSID", "Signal (dBm)", "Quality", "Channel"))
            print("============================================================")
            
            if let networks = networks, networks.count > 0 {
                let sorted = networks.sorted { $0.rssiValue ?? -100 > $1.rssiValue ?? -100 }
                
                for network in sorted {
                    let ssid = network.ssid ?? "Unknown"
                    let rssi = network.rssiValue ?? -100
                    let channel = network.wlanChannel?.channelNumber ?? 0
                    
                    // Quality indicator
                    var quality = "●●●●●"
                    if rssi <= -90 {
                        quality = "●○○○○ Very Weak"
                    } else if rssi <= -80 {
                        quality = "●●○○○ Weak"
                    } else if rssi <= -70 {
                        quality = "●●●○○ Fair"
                    } else if rssi <= -67 {
                        quality = "●●●●○ Good"
                    } else {
                        quality = "●●●●● Excellent"
                    }
                    
                    print(String(format: "%-25s %-12d %-15s %-10d", ssid, rssi, quality, channel))
                }
                print("============================================================")
                print()
                
                // Save to JSON
                let jsonData: [[String: Any]] = sorted.map { network in
                    [
                        "SSID": network.ssid ?? "Unknown",
                        "RSSI": network.rssiValue ?? -100,
                        "Channel": network.wlanChannel?.channelNumber ?? 0,
                        "BSSID": network.bssid ?? "Unknown",
                        "Security": network.security.description
                    ]
                }
                
                let jsonDict: [String: Any] = [
                    "networks": jsonData,
                    "scan_time": ISO8601DateFormatter().string(from: Date())
                ]
                
                if let json = try? JSONSerialization.data(withJSONObject: jsonDict, options: .prettyPrinted) {
                    try? json.write(to: URL(fileURLWithPath: "wifi_real_networks.json"))
                    print("✓ Data saved to wifi_real_networks.json")
                }
            }
        } else {
            print("Could not access WiFi interface. Make sure WiFi is enabled.")
        }
    } catch {
        print("Error scanning networks: \(error)")
    }
}

scanWiFiNetworks()
