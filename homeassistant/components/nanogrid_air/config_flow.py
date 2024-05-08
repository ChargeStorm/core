"""Config flow for Nanogrid Air integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL

from .api import fetch_mac, get_ip
from .const import DOMAIN

API_DEFAULT = "http://ctek-ng-air.local/"
IP_DEFAULT = "Delete me and enter device's IP"
TITLE = "Nanogrid Air"


class NanogridAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nanogrid Air integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._url = API_DEFAULT

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        self._async_abort_entries_match()

        # Attempt to automatically detect the device
        if await get_ip():
            mac_address = await fetch_mac()
            if mac_address:
                unique_id = mac_address
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=TITLE,
                    data={CONF_URL: self._url},
                )

        # If automatic detection fails, ask for user input
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Optional(CONF_URL, default=IP_DEFAULT): str,
                    }
                ),
            )

        # Use the manually provided IP to attempt connection again
        if await get_ip(user_input[CONF_URL]):
            mac_address = await fetch_mac()
            if mac_address:
                unique_id = mac_address
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=TITLE,
                    data={CONF_URL: user_input[CONF_URL]},
                )
        return self.async_abort(reason="not_responding")
