"""Config flow for Nanogrid Air integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL

from .api import fetch_meter_data, fetch_status_data
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

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_URL, default=API_DEFAULT): str,
                    }
                ),
            )

        mac_address = await fetch_status_data()
        await self.async_set_unique_id(mac_address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title="Nanogrid Air", data={"url": self._url})

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle Zeroconf discovery."""

        self._url = f"http://{discovery_info.host}/meter/"
        return await fetch_meter_data()
