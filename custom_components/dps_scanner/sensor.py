"""Sensor platform for DPS Scanner."""
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import tinytuya

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DPS Scanner sensors."""
    device_id = config_entry.data.get("device_id")
    ip = config_entry.data.get("ip")
    local_key = config_entry.data.get("local_key")
    version = config_entry.data.get("version", "3.3")
    
    sensors = [
        TuyaDeviceStatusSensor(hass, device_id, ip, local_key, version),
        TuyaDeviceDPSSensor(hass, device_id, ip, local_key, version),
    ]
    
    async_add_entities(sensors, True)


class TuyaDeviceStatusSensor(SensorEntity):
    """Sensor showing the connection status of a Tuya device."""

    def __init__(self, hass, device_id, ip, local_key, version):
        """Initialize the sensor."""
        self.hass = hass
        self._device_id = device_id
        self._ip = ip
        self._local_key = local_key
        self._version = version
        self._attr_name = f"Tuya {device_id[:8]} Status"
        self._attr_unique_id = f"{device_id}_status"
        self._attr_icon = "mdi:wifi"
        self._state = "unknown"
        self._attributes = {}

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self):
        """Update the sensor."""
        try:
            d = await self.hass.async_add_executor_job(
                lambda: tinytuya.OutletDevice(
                    dev_id=self._device_id,
                    address=self._ip,
                    local_key=self._local_key,
                    version=float(self._version)
                )
            )
            
            data = await self.hass.async_add_executor_job(d.status)
            
            if data and "Error" not in data:
                self._state = "online"
                self._attr_icon = "mdi:wifi"
                self._attributes = {
                    "device_id": self._device_id,
                    "ip_address": self._ip,
                    "protocol_version": self._version,
                    "last_update": data.get("t", "unknown"),
                }
            else:
                self._state = "error"
                self._attr_icon = "mdi:wifi-alert"
                self._attributes = {
                    "device_id": self._device_id,
                    "ip_address": self._ip,
                    "error": data.get("Error", "Unknown error") if data else "No response",
                }
        except Exception as e:
            _LOGGER.error(f"Failed to update status for {self._device_id}: {e}")
            self._state = "offline"
            self._attr_icon = "mdi:wifi-off"
            self._attributes = {
                "device_id": self._device_id,
                "ip_address": self._ip,
                "error": str(e),
            }


class TuyaDeviceDPSSensor(SensorEntity):
    """Sensor showing all DPS values of a Tuya device."""

    def __init__(self, hass, device_id, ip, local_key, version):
        """Initialize the sensor."""
        self.hass = hass
        self._device_id = device_id
        self._ip = ip
        self._local_key = local_key
        self._version = version
        self._attr_name = f"Tuya {device_id[:8]} DPS"
        self._attr_unique_id = f"{device_id}_dps"
        self._attr_icon = "mdi:code-json"
        self._state = 0
        self._attributes = {}

    @property
    def state(self):
        """Return the number of DPS found."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return all DPS as attributes."""
        return self._attributes

    async def async_update(self):
        """Update the sensor."""
        try:
            d = await self.hass.async_add_executor_job(
                lambda: tinytuya.OutletDevice(
                    dev_id=self._device_id,
                    address=self._ip,
                    local_key=self._local_key,
                    version=float(self._version)
                )
            )
            
            data = await self.hass.async_add_executor_job(d.status)
            
            if data and "dps" in data:
                dps = data["dps"]
                self._state = len(dps)
                self._attributes = {
                    "device_id": self._device_id,
                    "dps_values": dps,
                    "raw_response": str(data),
                }
            else:
                self._state = 0
                self._attributes = {
                    "device_id": self._device_id,
                    "error": "No DPS data available",
                }
        except Exception as e:
            _LOGGER.error(f"Failed to update DPS for {self._device_id}: {e}")
            self._state = 0
            self._attributes = {
                "device_id": self._device_id,
                "error": str(e),
            }
