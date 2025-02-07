"""Test the Nanogrid Air config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.components.nanogrid_air.const import DOMAIN
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


@pytest.mark.parametrize(
    (
        "get_ip_return",
        "fetch_mac_return",
        "result_type",
        "title",
        "data",
        "expected_errors",
    ),
    [
        (
            True,
            "00:11:22:33:44:55",
            FlowResultType.CREATE_ENTRY,
            "Nanogrid Air",
            {CONF_URL: "http://ctek-ng-air.local/meter/"},
            None,
        ),
        (False, None, FlowResultType.FORM, None, None, {"base": "cannot_connect"}),
        (True, None, FlowResultType.FORM, None, None, {"base": "invalid_auth"}),
        (
            False,
            "00:11:22:33:44:55",
            FlowResultType.FORM,
            None,
            None,
            {"base": "cannot_connect"},
        ),
    ],
)
async def test_form_auto_detect(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    get_ip_return,
    fetch_mac_return,
    result_type,
    title,
    data,
    expected_errors,
) -> None:
    """Test auto-detect scenarios with different return values."""
    with (
        patch(
            "homeassistant.components.nanogrid_air.config_flow.get_ip",
            return_value=get_ip_return,
        ),
        patch(
            "homeassistant.components.nanogrid_air.config_flow.fetch_mac",
            return_value=fetch_mac_return,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.async_block_till_done()

    assert result["type"] == result_type
    if result_type == FlowResultType.CREATE_ENTRY:
        assert result["title"] == title
        assert result["data"] == data
        assert len(mock_setup_entry.mock_calls) == 1
    else:
        assert result["errors"] == expected_errors


async def test_form_manual_entry_success(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test manual entry success."""
    user_input = {CONF_URL: "http://user-provided-url.local/meter/"}
    with (
        patch(
            "homeassistant.components.nanogrid_air.config_flow.get_ip",
            return_value=True,
        ),
        patch(
            "homeassistant.components.nanogrid_air.config_flow.fetch_mac",
            return_value="00:11:22:33:44:55",
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Nanogrid Air"
    assert result["data"][CONF_URL] == "http://user-provided-url.local/meter/"
    assert len(mock_setup_entry.mock_calls) == 1

    assert CONF_URL in result["data"]


async def test_form_not_responding(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test device not responding."""
    with patch(
        "homeassistant.components.nanogrid_air.config_flow.get_ip", return_value=False
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_form_invalid_mac(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test invalid MAC address handling."""
    with (
        patch(
            "homeassistant.components.nanogrid_air.config_flow.get_ip",
            return_value=True,
        ),
        patch(
            "homeassistant.components.nanogrid_air.config_flow.fetch_mac",
            return_value=None,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


@pytest.mark.parametrize(
    ("get_ip_return", "fetch_mac_return", "expected_errors"),
    [
        (False, None, {"base": "cannot_connect"}),
        (True, None, {"base": "invalid_auth"}),
    ],
)
async def test_form_error_handling(
    hass: HomeAssistant, get_ip_return, fetch_mac_return, expected_errors
) -> None:
    """Test handling various error scenarios."""
    user_input = {CONF_URL: "http://user-provided-url.local/meter/"}
    with (
        patch(
            "homeassistant.components.nanogrid_air.config_flow.get_ip",
            return_value=get_ip_return,
        ),
        patch(
            "homeassistant.components.nanogrid_air.config_flow.fetch_mac",
            return_value=fetch_mac_return,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == expected_errors


async def test_form_network_failure(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test handling network failures."""
    with patch(
        "homeassistant.components.nanogrid_air.config_flow.get_ip",
        side_effect=ConnectionError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_form_user_input_exception(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test exception handling during user input."""
    user_input = {CONF_URL: "http://user-provided-url.local/meter/"}

    with (
        patch(
            "homeassistant.components.nanogrid_air.config_flow.get_ip",
            side_effect=Exception("Test exception"),
        ),
        patch(
            "homeassistant.components.nanogrid_air.config_flow.fetch_mac",
            return_value="00:11:22:33:44:55",
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "not_responding"


async def test_form_user_input_connection_error(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test handling ConnectionError during user input."""
    user_input = {CONF_URL: "http://user-provided-url.local/meter/"}

    with (
        patch(
            "homeassistant.components.nanogrid_air.config_flow.get_ip",
            side_effect=ConnectionError,
        ),
        patch(
            "homeassistant.components.nanogrid_air.config_flow.fetch_mac",
            return_value="00:11:22:33:44:55",
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "not_responding"
