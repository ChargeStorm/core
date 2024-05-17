"""Fetch API for Nanogrid Air."""

import socket

import aiohttp

from homeassistant.core import _LOGGER

device_ip: str | None = None


async def get_ip(users_ip=None):
    """Fetch IP address from hostname."""
    if users_ip:
        globals()["device_ip"] = users_ip
        return True

    try:
        ip = socket.gethostbyname("ctek-ng-air.local")
        if ip:
            _LOGGER.debug("Resolved IP: %s", ip)
            globals()["device_ip"] = ip
            _LOGGER.debug("Device IP: %s", globals()["device_ip"])
            return True
    except socket.gaierror as e:
        _LOGGER.error("Failed to resolve hostname: %s", e)
        return False


async def fetch_mac():
    """Fetch mac address from status API."""
    url_status = f"http://{device_ip}/status/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_status) as api_status_response:
                api_status_response.raise_for_status()
                mac = await api_status_response.json()
                return mac["deviceInfo"]["mac"]
        except aiohttp.ClientError as exc:
            _LOGGER.error("HTTP client error occurred: %s", exc)
            await get_ip()
            return {}
        except aiohttp.HttpProcessingError as exc:
            _LOGGER.error(
                "HTTP request error occurred: %s - %s", exc.status, exc.message
            )
            return {}


async def fetch_meter_data():
    """Fetch data from the API and return as a dictionary."""
    url_meter = f"http://{device_ip}/meter/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_meter) as api_meter_response:
                api_meter_response.raise_for_status()
                return await api_meter_response.json()
        except aiohttp.ClientError as exc:
            _LOGGER.error("HTTP client error occurred: %s", exc)
            await get_ip()
            return {}
        except aiohttp.HttpProcessingError as exc:
            _LOGGER.error(
                "HTTP request error occurred: %s - %s", exc.status, exc.message
            )
            return {}
