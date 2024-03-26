"""Support for mDNS discovery."""
# This file is responsible for the mDNS discovery of the CTEK device.
# It is capable of discovering the CTEK mdns service _nghome._tcp.local.
# It is also capable of creating and publishing the CTEK mdns service _nghome._tcp.local.


import asyncio
import socket

from zeroconf import ServiceBrowser, ServiceInfo, ServiceStateChange

from homeassistant.components.zeroconf import async_get_instance
from homeassistant.core import HomeAssistant


async def discover_service(
    hass: HomeAssistant, service_type="_nghome._tcp.local.", timeout=1
) -> None | str:
    """Discover mDNS service and return IP address."""

    zc = await async_get_instance(hass)

    discovered_ip: asyncio.Future = asyncio.Future()

    def service_update(zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and not discovered_ip.done():
                discovered_ip.set_result(socket.inet_ntoa(info.addresses[0]))

    ServiceBrowser(zc, service_type, handlers=[service_update])

    try:
        return await asyncio.wait_for(discovered_ip, timeout=timeout)
    except TimeoutError:
        return None


async def create_and_publish_service(
    hass: HomeAssistant, service_type="_nghome._tcp.local.", ip="127.0.0.1", port=1883
) -> None | str:
    """Create and publish a mDNS service."""

    zc = await async_get_instance(hass)

    info = ServiceInfo(
        service_type,
        "example._nghome._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={"property_key": "property_value"},
        server="example.local.",
    )
    await hass.async_add_executor_job(zc.register_service, info)

    return None
