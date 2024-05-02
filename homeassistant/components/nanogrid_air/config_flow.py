"""Config flow for Nanogrid Air integration."""

from __future__ import annotations

from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.exceptions import ConfigEntryNotReady

from .api import _LOGGER, fetch_mac, fetch_meter_data
from .const import DOMAIN

API_DEFAULT = "http://ctek-ng-air.local/meter/"


class NanogridAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nanogrid Air integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._url = API_DEFAULT

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""

        self._async_abort_entries_match()

        try:
            mac_address = await fetch_mac()
            unique_id = mac_address
        except ConfigEntryNotReady as e:
            _LOGGER.error("Configuration step failed: %s", e)
            return self.async_abort(reason=str(e))

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title="Nanogrid Air", data={"url": self._url})

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle Zeroconf discovery."""
        self._url = f"http://{discovery_info.host}/meter/"
        try:
            entity_data = await fetch_meter_data()
            return self.async_create_entry(
                title="Nanogrid Air", data={"entity_data": entity_data}
            )
        except ConfigEntryNotReady as e:
            _LOGGER.error("Zeroconf discovery failed: %s", e)
            return self.async_abort(reason=str(e))
