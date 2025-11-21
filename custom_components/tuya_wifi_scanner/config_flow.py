"""Config flow for Tuya WiFi Scanner integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import tinytuya

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TuyaWifiScannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya WiFi Scanner."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.devices = {}
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step - scan for devices."""
        errors = {}

        if user_input is None:
            # Show the scan button
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "info": "Click Submit to scan for Tuya devices on your network."
                },
            )

        # Perform the scan
        try:
            _LOGGER.info("Starting Tuya device scan...")
            
            # deviceScan takes (verbose=bool, maxretry=int) parameters
            # Returns a dictionary with IP addresses as keys
            devices = await self.hass.async_add_executor_job(
                lambda: tinytuya.deviceScan(False, 20)
            )
            
            if not devices:
                errors["base"] = "no_devices_found"
                _LOGGER.warning("No Tuya devices found on network")
            else:
                self.devices = devices
                _LOGGER.info(f"Found {len(devices)} Tuya device(s)")
                return await self.async_step_select_device()

        except Exception as e:
            _LOGGER.error(f"Scan failed: {e}", exc_info=True)
            errors["base"] = "scan_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    async def async_step_select_device(self, user_input=None):
        """Let the user select a discovered device."""
        if user_input is not None:
            device_ip = user_input["device"]
            self.selected_device = {
                "ip": device_ip,
                **self.devices[device_ip]
            }
            return await self.async_step_device_key()

        # Get list of already configured device IDs
        configured_devices = {
            entry.data.get("device_id")
            for entry in self._async_current_entries()
        }

        # Create a list of devices for selection, filtering out already configured ones
        # deviceScan returns dict with IP as key and device info as value
        device_options = {}
        for ip, dev_info in self.devices.items():
            dev_id = dev_info.get("gwId", "Unknown ID")
            
            # Skip if already configured
            if dev_id in configured_devices:
                _LOGGER.debug(f"Skipping already configured device: {dev_id}")
                continue
                
            version = dev_info.get("version", "Unknown")
            device_options[ip] = f"{dev_id} ({ip}) - v{version}"

        # If no new devices found, abort
        if not device_options:
            return self.async_abort(reason="no_new_devices")

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): vol.In(device_options),
                }
            ),
        )

    async def async_step_device_key(self, user_input=None):
        """Ask the user for the device key and validate it."""
        errors = {}

        if user_input is not None:
            local_key = user_input["local_key"]
            device_id = self.selected_device.get("gwId")
            ip = self.selected_device.get("ip")
            version = self.selected_device.get("version", "3.3")
            
            # Validate the key by attempting to connect
            try:
                _LOGGER.info(f"Attempting to connect to device {device_id} at {ip}")
                
                # Test connection with provided key
                d = await self.hass.async_add_executor_job(
                    lambda: tinytuya.OutletDevice(
                        dev_id=device_id,
                        address=ip,
                        local_key=local_key,
                        version=float(version)
                    )
                )
                
                # Try to get status to validate the key
                data = await self.hass.async_add_executor_job(d.status)
                
                if data and "Error" in data:
                    _LOGGER.error(f"Connection test failed: {data['Error']}")
                    errors["local_key"] = "invalid_key"
                else:
                    _LOGGER.info(f"Successfully connected to device {device_id}")
                    # Key is valid, create the entry
                    return self.async_create_entry(
                        title=f"Tuya Device {device_id[:12]}",
                        data={
                            "device_id": device_id,
                            "ip": ip,
                            "local_key": local_key,
                            "version": version,
                        },
                    )
                    
            except Exception as e:
                _LOGGER.error(f"Failed to validate device key: {e}", exc_info=True)
                errors["local_key"] = "cannot_connect"

        return self.async_show_form(
            step_id="device_key",
            data_schema=vol.Schema(
                {
                    vol.Required("local_key"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "device_id": self.selected_device.get("gwId", "Unknown"),
                "ip": self.selected_device.get("ip", "Unknown"),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TuyaOptionsFlowHandler(config_entry)


class TuyaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Tuya WiFi Scanner."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.options.get("scan_interval", 30),
                    ): int,
                }
            ),
        )
