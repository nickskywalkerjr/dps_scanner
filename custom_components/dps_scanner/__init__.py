"""The DPS Scanner integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from . import dps_scanner

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the DPS Scanner component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Setup DPS scanning services
    await dps_scanner.async_setup_services(hass)
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up DPS Scanner from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    _LOGGER.info(
        f"Tuya device configured: {entry.data.get('device_id')} at {entry.data.get('ip')}"
    )
    
    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
