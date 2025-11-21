"""Tuya WiFi Scanner integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tuya_wifi_scanner"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tuya WiFi Scanner from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store the scan results
    hass.data[DOMAIN][entry.entry_id] = entry.data.get("devices", [])
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
