# Tuya WiFi Scanner for Home Assistant

A Home Assistant custom integration that discovers, pairs, and reverse engineers Tuya WiFi devices on your local network. No cloud credentials needed for device discovery!

## 🌟 Features

### Device Discovery & Pairing
- **Local Network Scanning**: Automatically discovers Tuya devices on your LAN
- **Easy Device Pairing**: Simple step-by-step configuration flow
- **Key Validation**: Verifies your device local key before saving the configuration
- **Duplicate Prevention**: Filters out already configured devices during scanning
- **Protocol Support**: Compatible with Tuya protocol versions 3.1, 3.2, 3.3, 3.4, and 3.5

### DPS Reverse Engineering Tools
- **🔍 DPS Scanner**: Discover all available Data Points (DPS) on any Tuya device
- **📊 Real-Time Monitor**: Capture live DPS changes as you interact with devices
- **📝 Detailed Logging**: All results saved to JSON files for analysis
- **🎯 Multiple Detection Methods**: Uses various techniques to find hidden DPS

## 📋 Requirements

- Home Assistant (2023.1 or newer recommended)
- Tuya devices connected to your local network
- Local keys for your Tuya devices (obtained from Tuya IoT Platform)

## 🚀 Installation

### Manual Installation

1. Download or clone this repository
2. Copy the `tuya_wifi_scanner` folder to your Home Assistant `custom_components` directory:
   ```
   config/
   └── custom_components/
       └── tuya_wifi_scanner/
           ├── __init__.py
           ├── dps_scanner.py
           ├── manifest.json
           ├── const.py
           ├── config_flow.py
           ├── services.yaml
           ├── strings.json
           └── translations/
               └── en.json
   ```
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "Tuya WiFi Scanner"

## 🔧 Configuration

### Step 1: Get Your Device Local Keys

Before you can use this integration, you need to obtain the local keys for your Tuya devices:

#### Option A: Using TinyTuya Wizard (Recommended)
```bash
pip install tinytuya
python -m tinytuya wizard
```
Follow the wizard instructions to connect to Tuya IoT Platform and retrieve your device keys.

#### Option B: Manual Method via Tuya IoT Platform
1. Create an account on [iot.tuya.com](https://iot.tuya.com/)
2. Create a cloud project and link your Tuya/Smart Life app
3. Find your devices and copy their local keys

📚 For detailed instructions, see the [TinyTuya Setup Guide](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys).

### Step 2: Add Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration** and search for "Tuya WiFi Scanner"
3. Click **Submit** to start scanning for devices on your network
4. Select a device from the discovered list
5. Enter the local key for the selected device
6. The integration will validate the key and add the device if successful

## 🔍 Reverse Engineering Tuya Devices

This integration includes powerful tools to reverse engineer Tuya devices and discover their Data Points (DPS).

### What are DPS (Data Points)?

DPS are the individual controllable/readable attributes of a Tuya device. For example:
- DPS 1: Power switch (on/off)
- DPS 2: Mode (white/color/scene)
- DPS 3: Brightness (0-1000)
- DPS 20: Current temperature
- And many more...

### Service 1: Scan Device DPS

Discovers all available DPS and their current values.

**Usage in Developer Tools:**
```yaml
service: tuya_wifi_scanner.scan_device_dps
data:
  device_id: "bf1234567890abcdef"
```

**What it does:**
- Fetches current device status
- Probes common DPS IDs (1-29)
- Tries multiple detection methods
- Saves complete results to `config/tuya_dps_scan_[device_id].json`
- Shows notification with summary

**Example Output:**
```json
{
  "device_id": "bf1234567890abcdef",
  "ip": "192.168.1.100",
  "version": "3.3",
  "discovered_dps": {
    "1": true,
    "2": "white",
    "3": 500,
    "5": "00ff0000ffff",
    "20": 255
  }
}
```

### Service 2: Monitor Device Real-Time

Captures all DPS changes as they happen - perfect for discovering what each control does!

**Usage in Developer Tools:**
```yaml
service: tuya_wifi_scanner.monitor_device_realtime
data:
  device_id: "bf1234567890abcdef"
  duration: 120  # Monitor for 2 minutes
```

**What it does:**
- Opens persistent connection to device
- Captures ALL DPS changes in real-time
- Logs exact values and timestamps
- Saves detailed event log to `config/tuya_monitor_[device_id]_[timestamp].json`

**How to use it:**
1. Start the monitoring service
2. Interact with your device (press buttons, change settings, etc.)
3. Check the generated JSON file to see which DPS changed

**Example Output:**
```json
[
  {
    "timestamp": 1234567890.123,
    "data": {
      "dps": {
        "1": true
      }
    }
  },
  {
    "timestamp": 1234567892.456,
    "data": {
      "dps": {
        "3": 750
      }
    }
  }
]
```

## 🎯 Reverse Engineering Workflow

Follow this process to completely map out your Tuya device:

### 1. Initial Discovery
```yaml
service: tuya_wifi_scanner.scan_device_dps
data:
  device_id: "your_device_id"
```
This gives you a baseline of all available DPS.

### 2. Interactive Testing
```yaml
service: tuya_wifi_scanner.monitor_device_realtime
data:
  device_id: "your_device_id"
  duration: 120
```

While monitoring runs:
- Turn device on/off
- Change brightness
- Switch modes
- Adjust color/temperature
- Try all buttons and features
- Change any settings in the app

### 3. Analyze Results

Open the generated JSON files in your Home Assistant config folder:
- `tuya_dps_scan_[device_id].json` - Shows all DPS and current values
- `tuya_monitor_[device_id]_[timestamp].json` - Shows what changed during monitoring

### 4. Map DPS to Functions

Create a table documenting what you discovered:

| DPS | Function | Type | Range | Notes |
|-----|----------|------|-------|-------|
| 1 | Power | bool | True/False | Main switch |
| 2 | Mode | enum | white/color/scene | Light mode |
| 3 | Brightness | int | 10-1000 | Brightness level |
| 5 | Color | string | RRGGBB format | RGB color |

### 5. Use in Automations

Now you can control your device with full knowledge:
```yaml
service: tuya_wifi_scanner.set_dps  # Example
data:
  device_id: "your_device_id"
  dps_id: 3
  value: 500  # Set brightness to 50%
```

## 🎓 Real-World Examples

### Example 1: Unknown Smart Bulb

**Goal:** Figure out how to control an unlabeled Chinese smart bulb

1. Run DPS scan - discovers DPS 1, 2, 3, 5, 20
2. Start monitoring for 60 seconds
3. Turn bulb on → DPS 1 changes to `true`
4. Change to color mode → DPS 2 changes to `"colour"`
5. Adjust brightness → DPS 3 changes from 10 to 1000
6. Pick red color → DPS 5 changes to `"ff0000"`

**Result:** Complete understanding of device control!

### Example 2: Smart Plug with Energy Monitoring

**Goal:** Find hidden energy monitoring features

1. Run DPS scan - discovers DPS 1, 18, 19, 20
2. Monitor while turning on a lamp
3. DPS 18 shows current (mA)
4. DPS 19 shows power (W)
5. DPS 20 shows voltage (V)

**Result:** Can now create energy monitoring dashboards!

### Example 3: Smart Thermostat

**Goal:** Understand all available settings

1. Scan discovers 20+ DPS points
2. Monitor while changing temperature → Find temp setpoint DPS
3. Change mode → Discover mode DPS (heat/cool/auto)
4. Enable schedule → Find schedule DPS
5. Adjust fan → Locate fan control DPS

**Result:** Full thermostat control with all features!

## 🛠️ Technical Details

### Supported Device Types

This integration can discover and analyze:
- Smart plugs and outlets
- Light bulbs and LED strips
- Switches and dimmers
- Covers and blinds
- Thermostats and climate devices
- Sensors (when awake)
- Fans and air purifiers
- Any Tuya WiFi-enabled device

### Network Requirements

- Devices must be on the same network/VLAN as Home Assistant
- UDP ports 6666, 6667, and 7000 must be open for discovery
- TCP port 6668 must be accessible for device communication
- Firewall rules should allow multicast/broadcast traffic

### DPS Detection Methods

The integration uses multiple techniques:

1. **Status Query**: Gets current state of all active DPS
2. **Sequential Probing**: Tests common DPS IDs (1-29)
3. **Available DPS Detection**: Uses TinyTuya's built-in detection
4. **Real-Time Monitoring**: Captures changes during device interaction

### Output Files

All scan results are saved to your Home Assistant config folder:

- `tuya_dps_scan_[device_id].json` - Complete DPS discovery results
- `tuya_monitor_[device_id]_[timestamp].json` - Real-time monitoring logs

## 📚 Integration with Other Tools

This integration works great alongside:

- **[LocalTuya](https://github.com/rospogrigio/localtuya-homeassistant)**: Use this scanner to discover devices and DPS, then add them to LocalTuya for full control
- **[TinyTuya](https://github.com/jasonacox/tinytuya)**: The underlying library that powers this integration
- **Native Tuya Integration**: Use for cloud features while keeping local discovery
- **Node-RED**: Use discovered DPS in custom flows
- **ESPHome**: Reference DPS mappings when creating custom integrations

## 🎯 Use Cases

### For Home Users
- **Identify Unknown Devices**: Figure out what DPS control your devices
- **Custom Automations**: Use hidden features not exposed in apps
- **Device Repair**: Troubleshoot devices by seeing actual state
- **Better Control**: Access advanced features the app doesn't show

### For Developers
- **Integration Development**: Map DPS before building integrations
- **Device Testing**: Validate device behavior and responses
- **Documentation**: Create accurate device documentation
- **Debugging**: Diagnose device communication issues

### For Reverse Engineers
- **Protocol Analysis**: Study Tuya device communication
- **Feature Discovery**: Find undocumented capabilities
- **Compatibility Testing**: Test devices across protocol versions
- **Community Contribution**: Share DPS mappings with others

## ⚠️ Limitations

- **Battery-Powered Devices**: May only be visible during brief wake periods
- **Local Keys Required**: You must obtain keys from Tuya IoT Platform first
- **Single Connection**: Tuya devices only allow one TCP connection at a time
- **Key Changes**: Local keys reset when devices are removed/re-added to Smart Life app
- **Firmware Updates**: Some older firmware versions may have compatibility issues
- **Some DPS Hidden**: Not all DPS may respond to probing (manufacturer locked)

## 🐛 Troubleshooting

### No Devices Found During Scan

- Ensure devices are powered on and connected to WiFi
- Check that Home Assistant is on the same network/VLAN
- Verify firewall allows UDP multicast traffic
- Try increasing scan time (default is 20 retries)

### DPS Scan Returns Limited Results

- Some DPS only appear when device is in specific states
- Try running scan while device is: on, off, in different modes
- Use real-time monitoring while interacting with device
- Some manufacturers hide DPS from external queries

### Real-Time Monitor Shows No Data

- Ensure device isn't being used by Smart Life app (close app)
- Check that device supports persistent connections
- Verify correct protocol version for your device
- Try triggering device state changes during monitoring

### Invalid Key Error

- Verify the local key from Tuya IoT Platform
- Check if device was recently re-paired (key may have changed)
- Ensure device ID matches exactly
- Try updating device firmware via Smart Life app

## 📖 Common DPS Reference

Here are some commonly found DPS across Tuya devices:

### Smart Plugs
- DPS 1: Switch (bool)
- DPS 9: Countdown timer (int, seconds)
- DPS 18: Current (int, mA)
- DPS 19: Power (int, W)
- DPS 20: Voltage (int, V)

### Smart Bulbs
- DPS 1: Switch (bool)
- DPS 2: Mode (enum: white/colour/scene/music)
- DPS 3: Brightness (int, 10-1000)
- DPS 4: Color temperature (int, 0-1000)
- DPS 5: Color (string, HSV or RGB)

### Sensors
- DPS 1: Door/Window state (bool)
- DPS 2: Battery level state (enum: low/middle/high)
- DPS 3: Battery percentage (int, 0-100)
- DPS 101: Current temperature (int, °C × 10)
- DPS 102: Current humidity (int, %)

See [TinyTuya Documentation](https://github.com/jasonacox/tinytuya#tuya-data-points---dps-table) for comprehensive DPS tables.

## 🤝 Contributing

Contributions are welcome! This project was built to extract device discovery and reverse engineering capabilities from [TinyTuya](https://github.com/jasonacox/tinytuya).

### Ways to Contribute
- Share your DPS discoveries for different devices
- Report bugs or compatibility issues
- Suggest new reverse engineering features
- Improve documentation
- Submit pull requests

## 📄 License

This integration uses the [TinyTuya](https://github.com/jasonacox/tinytuya) library and follows its MIT license.

## 🙏 Credits

- **[TinyTuya](https://github.com/jasonacox/tinytuya)** by Jason Cox - The powerful library that makes this integration possible
- **[LocalTuya](https://github.com/rospogrigio/localtuya-homeassistant)** - Inspiration for local Tuya control
- **Tuya Community** - For reverse engineering and protocol documentation
- **All Contributors** - For device testing and DPS mapping

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nickskywalkerjr/tuya_wifi_scanner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nickskywalkerjr/tuya_wifi_scanner/discussions)
- **TinyTuya Documentation**: [https://github.com/jasonacox/tinytuya](https://github.com/jasonacox/tinytuya)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## 🌟 Star History

If this integration helped you reverse engineer your Tuya devices, consider giving it a star on GitHub!

---

**Note**: This is primarily a discovery and reverse engineering tool. For full device control in production, consider using it alongside LocalTuya or other mature Tuya integrations. Use the insights gained from this tool to properly configure those integrations!
