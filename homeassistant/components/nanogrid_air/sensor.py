"""Platform for Nanogrid Air sensor."""

from collections.abc import Callable
import json
import logging

from helpers.typing import UndefinedType

from homeassistant.components.mqtt import async_subscribe, async_wait_for_mqtt_client
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_UNIQUE_ID,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_STATE_TOPIC_CURRENT,
    CONF_STATE_TOPIC_POWER_IN,
    CONF_STATE_TOPIC_POWER_OUT,
    CONF_STATE_TOPIC_TOTAL_ENERGY_EXPORT,
    CONF_STATE_TOPIC_TOTAL_ENERGY_IMPORT,
    CONF_STATE_TOPIC_VOLTAGE,
    CONF_TOPIC_ACTIVE_POWER_IN,
    CONF_TOPIC_ACTIVE_POWER_OUT,
    CONF_TOPIC_CURRENT,
    CONF_TOPIC_NANOGRID_AIR,
    CONF_TOPIC_TOTAL_ENERGY_EXPORT,
    CONF_TOPIC_TOTAL_ENERGY_IMPORT,
    CONF_TOPIC_VOLTAGE,
)

_LOGGER = logging.getLogger(__name__)

SENSOR = {
    "current_0": SensorEntityDescription(
        key="current_0",
        name="Current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "current_1": SensorEntityDescription(
        key="current_1",
        name="Current L2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "current_2": SensorEntityDescription(
        key="current_2",
        name="Current L3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "voltage_0": SensorEntityDescription(
        key="voltage_0",
        name="Voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "voltage_1": SensorEntityDescription(
        key="voltage_1",
        name="Voltage L2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "voltage_2": SensorEntityDescription(
        key="voltage_2",
        name="Voltage L3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "power_in": SensorEntityDescription(
        key="power_in",
        name="Power IN",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:transmission-tower-import",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "power_out": SensorEntityDescription(
        key="power_out",
        name="Power OUT",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:transmission-tower-export",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "total_energy_import": SensorEntityDescription(
        key="total_energy_import",
        name="Total Energy Import",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:transmission-tower-import",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "total_energy_export": SensorEntityDescription(
        key="total_energy_export",
        name="Total Energy Export",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:transmission-tower-export",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities for the integration entry."""
    sensors = []

    for sensor_id, sensor_description in SENSOR.items():
        unique_id = f"{entry.data.get(CONF_UNIQUE_ID, 'default_unique_id')}_{sensor_description.key}"
        sensors.append(NanogridAirSensor(unique_id, sensor_id, sensor_description))

    async_add_entities(sensors, True)


class NanogridAirSensor(SensorEntity):
    """Platform class for Nanogrid Air."""

    def __init__(
        self, unique_id, sensor_id, sensor_description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = sensor_description
        self._unique_id = "NGA_" + unique_id
        self._sensor_id = sensor_id
        self._state = None
        self._power_in = None
        self._power_out = None
        self._total_energy_import = None
        self._total_energy_export = None
        self._currents = [None, None, None]
        self._voltages = [None, None, None]
        self._sub_state_handlers = {"meterdata": self._handle_meter_data}
        self._sub_states_nga: list[Callable] = []

    @property
    def native_value(self) -> None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> None:
        """Return a unique id."""
        return self._unique_id

    @property
    def name(self) -> str | UndefinedType | None:
        """Return the name of the sensor."""
        return self.entity_description.name

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the class of this device, from SensorDeviceClass."""
        return self.entity_description.device_class

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self.entity_description.native_unit_of_measurement

    @property
    def state_class(self) -> str | None:
        """Return the state class of this entity, if any."""
        return self.entity_description.state_class

    async def async_added_to_hass(self) -> None:
        """List to store subscription state handlers."""
        await async_wait_for_mqtt_client(self.hass)
        _LOGGER.info("MQTT client is ready")

        for topic_suffix_nga, handler in self._sub_state_handlers.items():
            topic = f"{CONF_TOPIC_NANOGRID_AIR}/+/{topic_suffix_nga}"
            _LOGGER.debug("Subscribing to topic: {topic}")
            self._sub_states_nga.append(
                await async_subscribe(self.hass, topic, handler)
            )

    async def async_will_remove_from_hass(self) -> None:
        """Cleanup before removal."""

        if self._sub_states_nga:
            for sub_state in self._sub_states_nga:
                sub_state()

    def _handle_meter_data(self, msg):
        _LOGGER.debug("Received MQTT message on %s: %s", msg.topic, msg.payload)
        try:
            payload = json.loads(msg.payload)

            if CONF_TOPIC_CURRENT in payload:
                self._currents = payload[CONF_TOPIC_CURRENT]
            if CONF_TOPIC_VOLTAGE in payload:
                self._voltages = payload[CONF_TOPIC_VOLTAGE]

            if CONF_TOPIC_ACTIVE_POWER_IN in payload:
                self._power_in = payload[CONF_TOPIC_ACTIVE_POWER_IN]
            if CONF_TOPIC_ACTIVE_POWER_OUT in payload:
                self._power_out = payload[CONF_TOPIC_ACTIVE_POWER_OUT]

            if CONF_TOPIC_TOTAL_ENERGY_IMPORT in payload:
                self._total_energy_import = payload[CONF_TOPIC_TOTAL_ENERGY_IMPORT]
            if CONF_TOPIC_TOTAL_ENERGY_EXPORT in payload:
                self._total_energy_export = payload[CONF_TOPIC_TOTAL_ENERGY_EXPORT]

            if isinstance(self._sensor_id, str):
                type_parts = self._sensor_id.split("_")

                if self._sensor_id.startswith(CONF_STATE_TOPIC_CURRENT):
                    index = (
                        int(type_parts[1])
                        if len(type_parts) > 1 and type_parts[1].isdigit()
                        else None
                    )
                    if index is not None:
                        self._state = self._currents[index]

                elif self._sensor_id.startswith(CONF_STATE_TOPIC_VOLTAGE):
                    index = (
                        int(type_parts[1])
                        if len(type_parts) > 1 and type_parts[1].isdigit()
                        else None
                    )
                    if index is not None:
                        self._state = self._voltages[index]

                elif self._sensor_id == CONF_STATE_TOPIC_POWER_IN:
                    self._state = payload.get("activePowerIn")
                elif self._sensor_id == CONF_STATE_TOPIC_POWER_OUT:
                    self._state = payload.get("activePowerOut")
                elif self._sensor_id == CONF_STATE_TOPIC_TOTAL_ENERGY_IMPORT:
                    self._state = payload.get("totalEnergyActiveImport")
                elif self._sensor_id == CONF_STATE_TOPIC_TOTAL_ENERGY_EXPORT:
                    self._state = payload.get("totalEnergyActiveExport")

            _LOGGER.debug("Updated entity state to {self._state}")

        except json.JSONDecodeError as e:
            _LOGGER.error(
                "Error decoding JSON from MQTT message: %s, Payload: %s",
                e.msg,
                msg.payload,
            )
        except TypeError as e:
            _LOGGER.error("Unexpected payload type: %s", str(e))

        self.async_write_ha_state()
