"""Common fixtures for the Nanogrid Air tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.nanogrid_air.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
async def setup_hass(hass: HomeAssistant | (None)) -> Generator[None, None, None]:
    """Provide a HomeAssistant instance for tests with necessary setup."""
    await async_setup_component(hass, "persistent_notification", {})
    return
