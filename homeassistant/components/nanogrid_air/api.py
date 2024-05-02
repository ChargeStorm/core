"""Fetch API for Nanogrid Air."""

import asyncio
import logging
import socket

import aiohttp

from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)


async def fetch_data(hostname="ctek-ng-air.local", retry_delay=1, max_retries=5):
    """Fetch IP, MAC address, and meter data from the Nanogrid Air device with retries."""
    attempts = 0
    while attempts < max_retries:
        try:
            ip = socket.gethostbyname(hostname)
            _LOGGER.debug("Resolved IP: %s", ip)

            async with aiohttp.ClientSession() as session:
                url_status = f"http://{ip}/status/"
                url_meter = f"http://{ip}/meter/"

                async with session.get(url_status) as response:
                    response.raise_for_status()
                    status_data = await response.json()
                    mac_address = status_data["deviceInfo"]["mac"]
                    _LOGGER.debug("MAC Address fetched: %s", mac_address)

                async with session.get(url_meter) as response:
                    response.raise_for_status()
                    meter_data = await response.json()
                    _LOGGER.debug("Meter data fetched: %s", meter_data)

                return mac_address, meter_data

        except (socket.gaierror, aiohttp.ClientConnectionError) as e:
            _LOGGER.error(
                "Error fetching data: %s. Attempt number: %s", e, attempts + 1
            )
            attempts += 1
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

    _LOGGER.error("Failed to connect to Nanogrid Air after %s attempts", max_retries)
    raise ConfigEntryNotReady(
        f"Failed to connect to Nanogrid Air after {max_retries} attempts."
    )
