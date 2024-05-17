"""Config flow for Nanogrid Air integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL

from .api import fetch_mac, get_ip
from .const import DOMAIN

API_DEFAULT = "http://ctek-ng-air.local/meter/"
TITLE = "Nanogrid Air"
USER_DESC = "description"


class NanogridAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nanogrid Air integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._url = API_DEFAULT

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        self._async_abort_entries_match()

        errors = {}

        data_schema = vol.Schema(
            {vol.Required(CONF_URL, default=self._url, description=USER_DESC): str}
        )

        # Attempt to automatically detect the device
        if user_input is None:
            try:
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
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
            except ConnectionError:
                errors["base"] = "cannot_connect"

            return self.async_show_form(
                step_id="user",
                data_schema=data_schema,
                errors=errors,
            )

        # Handle user input
        try:
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
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "cannot_connect"
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except Exception:  # noqa: BLE001
            errors["base"] = "cannot_connect"
            return self.async_abort(reason="not_responding")

        return self.async_show_form(errors=errors)
