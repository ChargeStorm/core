"""Platform for Nanogrid Air sensor."""
from datetime import timedelta
import logging

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
from homeassistant.helpers.typing import UndefinedType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import fetch_meter_data

_LOGGER = logging.getLogger(__name__)

SENSOR = {
    "current_0": SensorEntityDescription(
        key="current_0",
        name="Current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "current_1": SensorEntityDescription(
        key="current_1",
        name="Current L2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "current_2": SensorEntityDescription(
        key="current_2",
        name="Current L3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "voltage_0": SensorEntityDescription(
        key="voltage_0",
        name="Voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "voltage_1": SensorEntityDescription(
        key="voltage_1",
        name="Voltage L2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "voltage_2": SensorEntityDescription(
        key="voltage_2",
        name="Voltage L3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "power_in": SensorEntityDescription(
        key="power_in",
        name="Power IN",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "power_out": SensorEntityDescription(
        key="power_out",
        name="Power OUT",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "total_energy_import": SensorEntityDescription(
        key="total_energy_import",
        name="Total Energy Import",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "total_energy_export": SensorEntityDescription(
        key="total_energy_export",
        name="Total Energy Export",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor entities for the integration entry."""
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="nanogrid_air",
        update_method=fetch_meter_data,
        update_interval=timedelta(seconds=1),
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for sensor_id, sensor_description in SENSOR.items():
        unique_id = f"{entry.data.get(CONF_UNIQUE_ID, 'default_unique_id')}_{sensor_description.key}"
        sensors.append(
            NanogridAirSensor(coordinator, unique_id, sensor_id, sensor_description)
        )

    async_add_entities(sensors, True)
    _LOGGER.debug("Initial data fetched: %s", coordinator.data)


class NanogridAirSensor(CoordinatorEntity, SensorEntity):
    """Platform class for Nanogrid Air."""

    def __init__(
        self,
        coordinator,
        unique_id,
        sensor_id,
        sensor_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = sensor_description
        self._unique_id = unique_id
        self._sensor_id = sensor_id

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data is None:
            return None

        if self._sensor_id.startswith("current_"):
            index = int(self._sensor_id.split("_")[-1])
            return data.get("current", [None, None, None])[index]
        if self._sensor_id.startswith("voltage_"):
            index = int(self._sensor_id.split("_")[-1])
            return data.get("voltage", [None, None, None])[index]
        if self._sensor_id == "power_in":
            return data.get("activePowerIn", None)
        if self._sensor_id == "power_out":
            return data.get("activePowerOut", None)
        if self._sensor_id == "total_energy_import":
            return data.get("totalEnergyActiveImport", None)
        if self._sensor_id == "total_energy_export":
            return data.get("totalEnergyActiveExport", None)
        return None

    @property
    def unique_id(self) -> str:
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
    def state_class(self) -> SensorStateClass | str | None:
        """Return the state class of this entity, if any."""
        return self.entity_description.state_class
