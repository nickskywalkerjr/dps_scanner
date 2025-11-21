"""The Tuya WiFi Scanner integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from . import dps_scanner

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Tuya WiFi Scanner component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Setup DPS scanning services
    await dps_scanner.async_setup_services(hass)
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Tuya WiFi Scanner from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    _LOGGER.info(
        f"Tuya device configured: {entry.data.get('device_id')} at {entry.data.get('ip')}"
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
