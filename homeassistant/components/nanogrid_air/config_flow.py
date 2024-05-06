"""Config flow for Nanogrid Air integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .api import fetch_mac
from .const import DOMAIN

API_DEFAULT = "http://ctek-ng-air.local/"


class NanogridAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nanogrid Air integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._url = API_DEFAULT

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""

        self._async_abort_entries_match()

        mac_address = await fetch_mac()
        if any(mac_address):
            unique_id = mac_address
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
        else:
            return self.async_abort(reason="not_responding")

        return self.async_create_entry(title="Nanogrid Air", data={"url": self._url})
