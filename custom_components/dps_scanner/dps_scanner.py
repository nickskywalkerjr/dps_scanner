"""DPS Scanner for Tuya devices - Reverse engineer available data points."""
import logging
import json
import tinytuya
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tuya_wifi_scanner"

async def async_setup_services(hass: HomeAssistant):
    """Set up services for DPS scanning."""
    
    async def scan_device_dps(call: ServiceCall):
        """Service to scan a device and discover all available DPS."""
        device_id = call.data.get("device_id")
        
        # Find the config entry for this device
        config_entry = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get("device_id") == device_id:
                config_entry = entry
                break
        
        if not config_entry:
            _LOGGER.error(f"No config entry found for device {device_id}")
            return
        
        ip = config_entry.data.get("ip")
        local_key = config_entry.data.get("local_key")
        version = config_entry.data.get("version", "3.3")
        
        _LOGGER.info(f"Starting DPS scan for device {device_id} at {ip}")
        
        try:
            # Create device connection
            d = await hass.async_add_executor_job(
                lambda: tinytuya.OutletDevice(
                    dev_id=device_id,
                    address=ip,
                    local_key=local_key,
                    version=float(version)
                )
            )
            
            # Method 1: Get current status
            _LOGGER.info("Fetching device status...")
            status = await hass.async_add_executor_job(d.status)
            
            dps_info = {
                "device_id": device_id,
                "ip": ip,
                "version": version,
                "status": status,
                "discovered_dps": {},
                "scan_methods": {}
            }
            
            if status and "dps" in status:
                dps_info["discovered_dps"] = status["dps"]
                _LOGGER.info(f"Found DPS from status: {list(status['dps'].keys())}")
            
            # Method 2: Try detect_available_dps (if available)
            try:
                _LOGGER.info("Attempting to detect available DPS...")
                available_dps = await hass.async_add_executor_job(d.detect_available_dps)
                dps_info["scan_methods"]["detect_available_dps"] = available_dps
                _LOGGER.info(f"Detected available DPS: {available_dps}")
            except AttributeError:
                _LOGGER.debug("detect_available_dps method not available")
            except Exception as e:
                _LOGGER.debug(f"detect_available_dps failed: {e}")
            
            # Method 3: Try common DPS IDs
            _LOGGER.info("Probing common DPS IDs...")
            common_dps = list(range(1, 30))  # Try DPS 1-29
            probed_dps = {}
            
            for dps_id in common_dps:
                if dps_id not in dps_info["discovered_dps"]:
                    try:
                        # Try to read this DPS
                        d.set_dpsUsed({str(dps_id): None})
                        result = await hass.async_add_executor_job(d.status)
                        if result and "dps" in result and str(dps_id) in result["dps"]:
                            probed_dps[str(dps_id)] = result["dps"][str(dps_id)]
                            _LOGGER.debug(f"Found DPS {dps_id}: {result['dps'][str(dps_id)]}")
                    except Exception:
                        pass
            
            if probed_dps:
                dps_info["scan_methods"]["probed_dps"] = probed_dps
                _LOGGER.info(f"Found additional DPS from probing: {list(probed_dps.keys())}")
            
            # Save results to a file
            output_file = hass.config.path(f"tuya_dps_scan_{device_id}.json")
            
            def write_file():
                with open(output_file, "w") as f:
                    json.dump(dps_info, f, indent=2)
            
            await hass.async_add_executor_job(write_file)
            
            _LOGGER.info(f"DPS scan complete. Results saved to {output_file}")
            
            # Send persistent notification
            hass.components.persistent_notification.async_create(
                f"DPS scan complete for device {device_id}!\n\n"
                f"Found {len(dps_info['discovered_dps'])} DPS points.\n"
                f"Results saved to: {output_file}\n\n"
                f"DPS IDs: {', '.join(map(str, dps_info['discovered_dps'].keys()))}",
                title="Tuya DPS Scanner",
                notification_id=f"tuya_dps_scan_{device_id}"
            )
            
        except Exception as e:
            _LOGGER.error(f"DPS scan failed: {e}", exc_info=True)
            hass.components.persistent_notification.async_create(
                f"DPS scan failed for device {device_id}.\n\n"
                f"Error: {str(e)}",
                title="Tuya DPS Scanner Error",
                notification_id=f"tuya_dps_scan_error_{device_id}"
            )
    
    async def monitor_device_realtime(call: ServiceCall):
        """Service to monitor a device in real-time and log all DPS changes."""
        device_id = call.data.get("device_id")
        duration = call.data.get("duration", 60)  # Monitor for 60 seconds by default
        
        # Find the config entry for this device
        config_entry = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get("device_id") == device_id:
                config_entry = entry
                break
        
        if not config_entry:
            _LOGGER.error(f"No config entry found for device {device_id}")
            return
        
        ip = config_entry.data.get("ip")
        local_key = config_entry.data.get("local_key")
        version = config_entry.data.get("version", "3.3")
        
        _LOGGER.info(f"Starting real-time monitoring for device {device_id} for {duration} seconds")
        
        try:
            import asyncio
            import time
            
            # Create device with persistent connection
            d = await hass.async_add_executor_job(
                lambda: tinytuya.OutletDevice(
                    dev_id=device_id,
                    address=ip,
                    local_key=local_key,
                    version=float(version),
                    persist=True
                )
            )
            
            # Request initial status
            await hass.async_add_executor_job(lambda: d.status(nowait=True))
            
            all_dps_changes = []
            start_time = time.time()
            
            def monitor_loop():
                """Monitor loop that runs in executor."""
                while time.time() - start_time < duration:
                    data = d.receive()
                    if data:
                        _LOGGER.info(f"Received data: {data}")
                        all_dps_changes.append({
                            "timestamp": time.time(),
                            "data": data
                        })
                    else:
                        # Send heartbeat
                        d.heartbeat()
                    time.sleep(0.5)
            
            await hass.async_add_executor_job(monitor_loop)
            
            # Save monitoring results
            output_file = hass.config.path(f"tuya_monitor_{device_id}_{int(time.time())}.json")
            
            def write_file():
                with open(output_file, "w") as f:
                    json.dump(all_dps_changes, f, indent=2)
            
            await hass.async_add_executor_job(write_file)
            
            _LOGGER.info(f"Monitoring complete. Captured {len(all_dps_changes)} events. Saved to {output_file}")
            
            hass.components.persistent_notification.async_create(
                f"Real-time monitoring complete for device {device_id}!\n\n"
                f"Captured {len(all_dps_changes)} events over {duration} seconds.\n"
                f"Results saved to: {output_file}",
                title="Tuya Device Monitor",
                notification_id=f"tuya_monitor_{device_id}"
            )
            
        except Exception as e:
            _LOGGER.error(f"Monitoring failed: {e}", exc_info=True)
    
    # Register services
    hass.services.async_register(DOMAIN, "scan_device_dps", scan_device_dps)
    hass.services.async_register(DOMAIN, "monitor_device_realtime", monitor_device_realtime)
    
    _LOGGER.info("Tuya DPS scanner services registered")
