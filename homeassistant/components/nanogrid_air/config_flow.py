"""Config flow for Nanogrid Air integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class NanogridAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for your integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None) -> config_entries.ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict = {}

        if user_input is not None:
            return self.async_create_entry(title="Nanogrid Air", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("broker_choice"): vol.In(
                        {
                            "addon": "Use the Add-on MQTT broker",
                            "external": "Use an external MQTT broker",
                        }
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "description": "Choose whether to use the internal Add-On as a broker or specify an external broker."
            },
        )
