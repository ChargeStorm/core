"""Fetch API for Nanogrid Air."""

import logging
import socket

import aiohttp

from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)


async def fetch_data():
    """Fetch IP, MAC address, and meter data from the Nanogrid Air device."""
    hostname = "ctek-ng-air.local"
    try:
        ip = socket.gethostbyname(hostname)
        _LOGGER.debug("Resolved IP: %s", ip)
    except socket.gaierror as e:
        _LOGGER.error("Failed to resolve hostname: %s", e)
        raise ConfigEntryNotReady("Failed to resolve IP address for Nanogrid Air.")  # noqa: B904

    async with aiohttp.ClientSession() as session:
        url_status = f"http://{ip}/status/"
        url_meter = f"http://{ip}/meter/"

        try:
            async with session.get(url_status) as response:
                response.raise_for_status()
                status_data = await response.json()
                mac_address = status_data["deviceInfo"]["mac"]

            async with session.get(url_meter) as response:
                response.raise_for_status()
                meter_data = await response.json()

            return mac_address, meter_data
        except (aiohttp.ClientError, aiohttp.HttpProcessingError) as e:
            _LOGGER.error("HTTP error occurred: %s", e)
            raise ConfigEntryNotReady(f"HTTP error accessing Nanogrid Air at {ip}.")  # noqa: B904
