# Tuya WiFi Scanner for Home Assistant

A Home Assistant custom integration that discovers and pairs Tuya WiFi devices on your local network without requiring cloud credentials or the Tuya IoT Platform for device discovery.

## 🌟 Features

- **Local Network Scanning**: Automatically discovers Tuya devices on your LAN
- **Easy Device Pairing**: Simple step-by-step configuration flow
- **Key Validation**: Verifies your device local key before saving the configuration
- **Duplicate Prevention**: Filters out already configured devices during scanning
- **Protocol Support**: Compatible with Tuya protocol versions 3.1, 3.2, 3.3, 3.4, and 3.5
- **No Cloud Required for Discovery**: Scan and discover devices locally without cloud API calls

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
           ├── manifest.json
           ├── const.py
           ├── config_flow.py
           └── translations/
               └── en.json
   ```
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "Tuya WiFi Scanner"

## 🔧 Configuration

### Step 1: Get Your Device Local Keys

Before you can use this integration, you need to obtain the local keys for your Tuya devices:

1. **Using TinyTuya Wizard** (Recommended):
   ```bash
   pip install tinytuya
   python -m tinytuya wizard
   ```
   Follow the wizard instructions to connect to Tuya IoT Platform and retrieve your device keys.

2. **Manual Method via Tuya IoT Platform**:
   - Create an account on [iot.tuya.com](https://iot.tuya.com/)
   - Create a cloud project and link your Tuya/Smart Life app
   - Find your devices and copy their local keys

For detailed instructions, see the [TinyTuya Setup Guide](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys).

### Step 2: Add Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration** and search for "Tuya WiFi Scanner"
3. Click **Submit** to start scanning for devices on your network
4. Select a device from the discovered list
5. Enter the local key for the selected device
6. The integration will validate the key and add the device if successful

## 🎯 Use Cases

This integration is perfect for:

- **Initial Device Discovery**: Quickly find all Tuya devices on your network
- **Local Control Setup**: Pair devices for local-only control without cloud dependency
- **Network Troubleshooting**: Verify which Tuya devices are accessible on your LAN
- **Bulk Device Setup**: Efficiently configure multiple Tuya devices
- **Privacy-Focused Users**: Minimize cloud interactions after initial key retrieval

## 🔍 How It Works

1. **Network Scanning**: The integration broadcasts UDP packets on ports 6666, 6667, and 7000 to discover Tuya devices
2. **Device Detection**: Tuya devices respond with their Device ID, IP address, and protocol version
3. **Key Validation**: When you enter a local key, the integration attempts to connect and retrieve device status
4. **Configuration Storage**: Valid configurations are stored for use by other integrations or automations

## 🛠️ Technical Details

### Supported Device Types

This integration can discover:
- Smart plugs and outlets
- Light bulbs and LED strips
- Switches and dimmers
- Covers and blinds
- Sensors (when awake)
- And any other Tuya WiFi-enabled device

### Network Requirements

- Devices must be on the same network/VLAN as Home Assistant
- UDP ports 6666, 6667, and 7000 must be open for discovery
- TCP port 6668 must be accessible for device communication
- Firewall rules should allow multicast/broadcast traffic

### Protocols Supported

- Protocol 3.1 (legacy devices)
- Protocol 3.2
- Protocol 3.3 (most common)
- Protocol 3.4
- Protocol 3.5 (newest devices)

## 📚 Integration with Other Tools

This integration works great alongside:

- **[LocalTuya](https://github.com/rospogrigio/localtuya-homeassistant)**: Use this scanner to discover devices, then add them to LocalTuya for full control
- **[TinyTuya](https://github.com/jasonacox/tinytuya)**: The underlying library that powers this integration
- **Native Tuya Integration**: Use for cloud features while keeping local discovery

## ⚠️ Limitations

- **Battery-Powered Devices**: May only be visible during brief wake periods
- **Local Keys Required**: You must obtain keys from Tuya IoT Platform first
- **Single Connection**: Tuya devices only allow one TCP connection at a time
- **Key Changes**: Local keys reset when devices are removed/re-added to Smart Life app
- **Firmware Updates**: Some older firmware versions may have compatibility issues

## 🐛 Troubleshooting

### No Devices Found

- Ensure devices are powered on and connected to WiFi
- Check that Home Assistant is on the same network/VLAN
- Verify firewall allows UDP multicast traffic
- Try increasing scan time (default is 20 retries)

### Invalid Key Error

- Verify the local key from Tuya IoT Platform
- Check if device was recently re-paired (key may have changed)
- Ensure device ID matches exactly
- Try updating device firmware via Smart Life app

### Connection Failed

- Device may be in use by Smart Life app (close the app)
- Check network connectivity to device IP
- Verify correct protocol version for your device
- Restart the device and try again

## 🤝 Contributing

Contributions are welcome! This project was built to extract the device discovery portion from the excellent [TinyTuya](https://github.com/jasonacox/tinytuya) project.

## 📄 License

This integration uses the [TinyTuya](https://github.com/jasonacox/tinytuya) library and follows its MIT license.

## 🙏 Credits

- **[TinyTuya](https://github.com/jasonacox/tinytuya)** by Jason Cox - The powerful library that makes this integration possible
- **[LocalTuya](https://github.com/rospogrigio/localtuya-homeassistant)** - Inspiration for local Tuya control
- Tuya community for reverse engineering and documentation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nickskywalkerjr/tuya_wifi_scanner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nickskywalkerjr/tuya_wifi_scanner/discussions)
- **TinyTuya Documentation**: [https://github.com/jasonacox/tinytuya](https://github.com/jasonacox/tinytuya)

---

**Note**: This is a discovery and pairing tool. For full device control, consider using it alongside LocalTuya or other Tuya integrations.
