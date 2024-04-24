"""The Nanogrid Air integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nanogrid Air from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


@callback
def cancel_tasks(hass: HomeAssistant):
    """Cancel all ongoing tasks stored in hass.data[DOMAIN]['tasks']."""
    tasks = hass.data[DOMAIN].get("tasks", [])
    for task in tasks:
        if not task.done():
            task.cancel()
    hass.data[DOMAIN]["tasks"] = []
