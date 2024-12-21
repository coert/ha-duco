from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from dacite import from_dict
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfTime,
    CONCENTRATION_PARTS_PER_MILLION,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api.DTO.DeviceDTO import DeviceDTO
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__package__)


@dataclass(kw_only=True, frozen=True)
class DucoSensorEntityDescription(SensorEntityDescription):
    """Describes an Duco sensor entity."""

    key: str
    name: str | None = None
    type: str | None = None
    sensor_key: str | None = None
    exists_fn: Callable[[Any], bool] = lambda _: True
    value_fn: Callable[[Any], float | int | str | None] = lambda _: None


# Define the sensor types
SENSORS_DUCOBOX: tuple[DucoSensorEntityDescription, ...] = (
    DucoSensorEntityDescription(
        key="temp_oda",
        name="Temperature (Outdoor)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.info.Ventilation.Sensor.TempOda),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Sensor is not None
        and device.info.Ventilation.Sensor.TempOda is not None,
    ),
    DucoSensorEntityDescription(
        key="temp_sup",
        name="Temperature (Supply)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.info.Ventilation.Sensor.TempSup),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Sensor is not None
        and device.info.Ventilation.Sensor.TempOda is not None,
    ),
    DucoSensorEntityDescription(
        key="temp_eta",
        name="Temperature (Extract)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.info.Ventilation.Sensor.TempEta),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Sensor is not None
        and device.info.Ventilation.Sensor.TempOda is not None,
    ),
    DucoSensorEntityDescription(
        key="temp_eha",
        name="Temperature (Exhaust)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.info.Ventilation.Sensor.TempEha),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Sensor is not None
        and device.info.Ventilation.Sensor.TempOda is not None,
    ),
    DucoSensorEntityDescription(
        key="fan_speed_sup",
        name="Fan Speed (Supply)",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        value_fn=lambda device: _proc_speed(device.info.Ventilation.Fan.SpeedSup),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Fan is not None
        and device.info.Ventilation.Fan.SpeedSup is not None,
    ),
    DucoSensorEntityDescription(
        key="fan_speed_eha",
        name="Fan Speed (Exhaust)",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        value_fn=lambda device: _proc_speed(device.info.Ventilation.Fan.SpeedEha),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Fan is not None
        and device.info.Ventilation.Fan.SpeedEha is not None,
    ),
    DucoSensorEntityDescription(
        key="pressure_supply",
        name="Pressure (Supply)",
        icon="mdi:arrow-collapse-down",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        value_fn=lambda device: _proc_press(device.info.Ventilation.Fan.PressSup),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Fan is not None
        and device.info.Ventilation.Fan.PressSup is not None,
    ),
    DucoSensorEntityDescription(
        key="pressure_eha",
        name="Pressure (Exhaust)",
        icon="mdi:arrow-collapse-up",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        value_fn=lambda device: _proc_press(device.info.Ventilation.Fan.PressEha),
        exists_fn=lambda device: device.info.Ventilation is not None
        and device.info.Ventilation.Fan is not None
        and device.info.Ventilation.Fan.PressEha is not None,
    ),
)
SENSORS_ZONES: dict[str, tuple[DucoSensorEntityDescription, ...]] = {
    "BOX": (
        DucoSensorEntityDescription(
            key="mode",
            name="Ventilation Mode",
            sensor_key="Mode",
            type="BOX",
            value_fn=lambda node: node.Ventilation.Mode,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.Mode is not None,
        ),
        DucoSensorEntityDescription(
            key="state",
            name="Ventilation State",
            sensor_key="State",
            type="BOX",
            value_fn=lambda node: node.Ventilation.State,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.State is not None,
        ),
        DucoSensorEntityDescription(
            key="flow_lvl_tgt",
            name="Flow Level Target",
            sensor_key="FlowLvlTgt",
            type="BOX",
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.Ventilation.FlowLvlTgt,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.FlowLvlTgt is not None,
        ),
        DucoSensorEntityDescription(
            key="time_state_remain",
            name="Time State Remaining",
            sensor_key="TimeStateRemain",
            type="BOX",
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: node.Ventilation.TimeStateRemain,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.TimeStateRemain is not None,
        ),
        DucoSensorEntityDescription(
            key="time_state_end",
            name="Time State Ending",
            sensor_key="TimeStateEnd",
            type="BOX",
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: node.Ventilation.TimeStateEnd,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.TimeStateEnd is not None,
        ),
        DucoSensorEntityDescription(
            key="temp",
            name="Temerature",
            sensor_key="Temp",
            type="BOX",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: node.Sensor.Temp,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Temp is not None,
        ),
        DucoSensorEntityDescription(
            key="rh",
            name="Relative Humidity",
            sensor_key="Rh",
            type="BOX",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: node.Sensor.Rh,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Rh is not None,
        ),
        DucoSensorEntityDescription(
            key="iaq_rh",
            name="Humidity Air Quality",
            sensor_key="IaqRh",
            type="BOX",
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.Sensor.IaqRh,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.IaqRh is not None,
        ),
    ),
    "UCCO2": (
        DucoSensorEntityDescription(
            key="temp",
            name="Temerature",
            sensor_key="Temp",
            type="UCCO2",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: node.Sensor.Temp,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Temp is not None,
        ),
        DucoSensorEntityDescription(
            key="co2",
            name="CO₂",
            sensor_key="Co2",
            type="UCCO2",
            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
            device_class=SensorDeviceClass.CO2,
            value_fn=lambda node: node.Sensor.Co2,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Co2 is not None,
        ),
        DucoSensorEntityDescription(
            key="iaq_co2",
            name="CO₂ Air Quality",
            sensor_key="IaqCo2",
            type="UCCO2",
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.Sensor.IaqCo2,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.IaqCo2 is not None,
        ),
    ),
    "BSRH": (
        DucoSensorEntityDescription(
            key="temp",
            name="Temerature",
            sensor_key="Temp",
            type="BSRH",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: node.Sensor.Temp,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Temp is not None,
        ),
        DucoSensorEntityDescription(
            key="rh",
            name="Relative Humidity",
            sensor_key="Rh",
            type="BSRH",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: node.Sensor.Rh,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Rh is not None,
        ),
        DucoSensorEntityDescription(
            key="iaq_rh",
            name="Humidity Air Quality",
            sensor_key="IaqRh",
            type="BSRH",
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.Sensor.IaqRh,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.IaqRh is not None,
        ),
    ),
}


def _proc_temp(temp: float) -> float:
    return temp / 10.0


def _proc_speed(speed: int) -> int:
    return speed


def _proc_press(press: int) -> int:
    return press


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
    """Set up Duco sensor based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Ensure the coordinator has refreshed its data
    await coordinator.async_config_entry_first_refresh()
    device: DeviceDTO = from_dict(data_class=DeviceDTO, data=coordinator.data)

    async_add_entities(
        DucoSensorEntity(coordinator, device, description)
        for description in SENSORS_DUCOBOX
        if description.exists_fn(device)
    )

    for node in device.nodes:
        async_add_entities(
            DucoNodeSensorEntity(coordinator, node, description)
            for description in SENSORS_ZONES.get(node.General.Type, ())
            if description.exists_fn(node)
        )


class DucoSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an Duco sensor."""

    device: DeviceDTO | NodeDataDTO
    entity_description: DucoSensorEntityDescription

    def __init__(
        self,
        coordinator,
        device: DeviceDTO | NodeDataDTO,
        entity_description: DucoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.device = device
        self.entity_description = entity_description
        self._attr_name = f"{entity_description.name}"
        self._attr_unique_id = f"{device.id}_{entity_description.key}"
        self._update_device_data()

    @property
    def device_info(self) -> dict:
        """Return information to link this entity with the correct device."""
        return {
            "manufacturer": MANUFACTURER,
            "identifiers": {(DOMAIN, self.device.account_module_index)},
        }

    def _update_device_data(self):
        """Update the internal data from the coordinator."""
        # Assuming devices are updated in the coordinator data
        updated_device = from_dict(data_class=DeviceDTO, data=self.coordinator.data)  # type: ignore
        if updated_device.id == self.device.id:
            self.device = updated_device

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.device)  # type: ignore

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"Getting update from coordinator in sensor {self.name}.")
        self._update_device_data()
        super()._handle_coordinator_update()


class DucoNodeSensorEntity(DucoSensorEntity):
    """Representation of an Duco sensor for a node."""

    node: NodeDataDTO

    def __init__(
        self,
        coordinator,
        node: NodeDataDTO,
        entity_description: DucoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, node, entity_description)

        self.node = node
        self._attr_name = f"{node.General.Name} {entity_description.name}"
        self._attr_unique_id = f"{node.Node}_{entity_description.key}"
        self._update_node_data()

    def _update_node_data(self):
        """Update the internal data from the coordinator."""
        # Assuming devices are updated in the coordinator data
        updated_node = from_dict(data_class=NodeDataDTO, data=self.coordinator.data)  # type: ignore
        if updated_node.id == self.device.id:
            self.device = updated_node

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"Getting update from coordinator in sensor {self.name}.")
        self._update_node_data()
        super()._handle_coordinator_update()
