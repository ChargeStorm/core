"""Fetch API for Nanogrid Air."""

import socket

import aiohttp

device_ip: str | None = None


async def get_ip(users_ip=None):
    """Fetch IP address from hostname."""
    if users_ip:
        globals()["device_ip"] = users_ip
        return True

    try:
        ip = socket.gethostbyname("ctek-ng-air.local")
        if ip:
            globals()["device_ip"] = ip
            return True
    except socket.gaierror:
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
        except aiohttp.ClientError:
            return {}
        except aiohttp.HttpProcessingError:
            return {}


async def fetch_meter_data():
    """Fetch data from the API and return as a dictionary."""
    url_meter = f"http://{device_ip}/meter/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_meter) as api_meter_response:
                api_meter_response.raise_for_status()
                return await api_meter_response.json()
        except aiohttp.ClientError:
            await get_ip()
            return {}
        except aiohttp.HttpProcessingError:
            return {}
