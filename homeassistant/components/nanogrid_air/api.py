"""Fetch API for Nanogrid Air."""

import logging
import socket

import httpx

_LOGGER = logging.getLogger(__name__)


async def fetch_data():
    """Fetch data from the API and return as a dictionary."""

    try:
        ip = socket.gethostbyname("ctek-ng-air.local")
        _LOGGER.debug("Resolved IP: %s", ip)
    except socket.gaierror as e:
        _LOGGER.error("Failed to resolve hostname: %s", e)
        return

    url = f"http://{ip}/meter/"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            _LOGGER.error(
                "HTTP request error occurred: %s",
                {exc.response.status_code} - {exc.response.text},
            )
            _LOGGER.error(
                "HTTP status error occurred: %s",
                {exc.response.status_code} - {exc.response.text},
            )
            return {}
        except httpx.RequestError as exc:
            _LOGGER.error("HTTP request error occurred: %s", exc)
            return {}
