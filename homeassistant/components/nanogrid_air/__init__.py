"""The Nanogrid Air integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .discovery import create_and_publish_service, discover_service

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nanogrid Air from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    if "tasks" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["tasks"] = []

    discovered_ip = await discover_service(hass)
    if discovered_ip is not None:
        hass.data[DOMAIN]["discovered_ip"] = discovered_ip
    else:
        service_creation_task = await create_and_publish_service(hass)
        hass.data[DOMAIN]["tasks"].append(service_creation_task)

    entry.async_on_unload(
        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP, lambda event: cancel_tasks(hass)
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok


@callback
def cancel_tasks(hass: HomeAssistant):
    """Cancel all ongoing tasks stored in hass.data[DOMAIN]['tasks']."""
    tasks = hass.data[DOMAIN].get("tasks", [])
    for task in tasks:
        if not task.done():
            task.cancel()
    hass.data[DOMAIN]["tasks"] = []
