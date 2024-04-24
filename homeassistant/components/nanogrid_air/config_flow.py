"""Config flow for Nanogrid Air integration."""
from __future__ import annotations

from aiohttp import ClientError
import voluptuous as vol

from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import (
    CONN_CLASS_LOCAL_POLL,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_URL
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_METER,
    API_STATUS,
    DOMAIN,
    ERROR_NOT_RESPONDING,
    ERROR_SINGLE_INSTANCE_ALLOWED,
)


class NanogridAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nanogrid Air integration."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize flow."""
        self._url = API_METER

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""

        session = async_get_clientsession(self.hass)

        if self._async_current_entries():
            return self.async_abort(reason=ERROR_SINGLE_INSTANCE_ALLOWED)

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Optional(CONF_URL, default=API_METER): str,
                    }
                ),
            )

        mac_res = await session.get(API_STATUS)
        mac_res.raise_for_status()
        mac = await mac_res.json()
        mac_address = mac["deviceInfo"]["mac"]

        await self.async_set_unique_id(mac_address)
        self._abort_if_unique_id_configured()

        self._url = user_input[CONF_URL]
        return await self._test_connection()

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle Zeroconf discovery."""

        self._url = f"http://{discovery_info.host}/meter/"
        return await self._test_connection()

    async def _test_connection(self):
        """Attempt to connect to the Nanogrid Air device to confirm it's reachable."""
        session = async_get_clientsession(self.hass)
        try:
            response = await session.get(self._url)
            response.raise_for_status()

            return self.async_create_entry(
                title="Nanogrid Air", data={"url": self._url}
            )
        except ClientError:
            return self.async_abort(reason=ERROR_NOT_RESPONDING)
        except HomeAssistantError as ha_err:
            return self.async_abort(reason=str(ha_err))

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> NanogridAirOptionsFlowHandler:
        """Get the options flow for this handler."""
        return NanogridAirOptionsFlowHandler(config_entry)


class NanogridAirOptionsFlowHandler(OptionsFlow):
    """Handle a options flow for Nanogrid Air."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_URL,
                        default=self.config_entry.options.get(CONF_URL, API_METER),
                    ): str,
                }
            ),
        )
