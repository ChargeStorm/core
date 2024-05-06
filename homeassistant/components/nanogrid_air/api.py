"""Fetch API for Nanogrid Air."""

import logging
import socket

import aiohttp

_LOGGER = logging.getLogger(__name__)


async def get_ip():
    """Fetch IP address from hostname."""
    try:
        ip = socket.gethostbyname("ctek-ng-air.local")
        _LOGGER.debug("Resolved IP: %s", ip)
        return ip
    except socket.gaierror as e:
        _LOGGER.error("Failed to resolve hostname: %s", e)
        return


async def fetch_mac():
    """Fetch mac address from status API."""
    ip = await get_ip()

    url_status = f"http://{ip}/status/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_status) as api_status_response:
                api_status_response.raise_for_status()
                mac = await api_status_response.json()
                mac_address = mac["deviceInfo"]["mac"]
                return mac_address
        except aiohttp.ClientError as exc:
            _LOGGER.error("HTTP client error occurred in fetch_mac: %s", exc)
            return {}
        except aiohttp.HttpProcessingError as exc:
            _LOGGER.error(
                "HTTP request error occurred: %s - %s", exc.status, exc.message
            )
            return {}


async def fetch_meter_data():
    """Fetch data from the API and return as a dictionary."""
    ip = await get_ip()

    url_meter = f"http://{ip}/meter/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_meter) as api_meter_response:
                api_meter_response.raise_for_status()
                api_meter_data = await api_meter_response.json()
                return api_meter_data
        except aiohttp.ClientError as exc:
            _LOGGER.error("HTTP client error occurred in fetch_meter: %s", exc)
            return {}
        except aiohttp.HttpProcessingError as exc:
            _LOGGER.error(
                "HTTP request error occurred: %s - %s", exc.status, exc.message
            )
            return {}
