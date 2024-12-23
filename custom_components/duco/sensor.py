from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorStateClass
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

from . import DucoConfigEntry

from .const import LOGGER
from .api.DTO.InfoDTO import InfoDTO
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .entity import DucoEntity
from .coordinator import DucoDeviceUpdateCoordinator


@dataclass(kw_only=True, frozen=True)
class DucoBoxSensorEntityDescription(SensorEntityDescription):
    """Describes an Duco sensor entity."""

    enabled_fn: Callable[[InfoDTO], bool] = lambda data: True
    exists_fn: Callable[[InfoDTO], bool] = lambda _: True
    value_fn: Callable[[InfoDTO], float | int | str | None] = lambda _: None


@dataclass(kw_only=True, frozen=True)
class DucoNodeSensorEntityDescription(SensorEntityDescription):
    """Describes an Duco sensor entity."""

    sensor_key: str
    type: str
    enabled_fn: Callable[[NodeDataDTO], bool] = lambda data: True
    exists_fn: Callable[[NodeDataDTO], bool] = lambda _: True
    value_fn: Callable[[NodeDataDTO], float | int | str | None] = lambda _: None


# Define the sensor types
SENSORS_DUCOBOX: tuple[DucoBoxSensorEntityDescription, ...] = (
    DucoBoxSensorEntityDescription(
        key="temp_oda",
        name="Temperature (Outdoor)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.Ventilation.Sensor.TempOda),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Sensor is not None
        and device.Ventilation.Sensor.TempOda is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="temp_sup",
        name="Temperature (Supply)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.Ventilation.Sensor.TempSup),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Sensor is not None
        and device.Ventilation.Sensor.TempOda is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="temp_eta",
        name="Temperature (Extract)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.Ventilation.Sensor.TempEta),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Sensor is not None
        and device.Ventilation.Sensor.TempOda is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="temp_eha",
        name="Temperature (Exhaust)",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: _proc_temp(device.Ventilation.Sensor.TempEha),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Sensor is not None
        and device.Ventilation.Sensor.TempOda is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="fan_speed_sup",
        name="Fan Speed (Supply)",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        value_fn=lambda device: _proc_speed(device.Ventilation.Fan.SpeedSup),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Fan is not None
        and device.Ventilation.Fan.SpeedSup is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="fan_speed_eha",
        name="Fan Speed (Exhaust)",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        value_fn=lambda device: _proc_speed(device.Ventilation.Fan.SpeedEha),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Fan is not None
        and device.Ventilation.Fan.SpeedEha is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="pressure_supply",
        name="Pressure (Supply)",
        icon="mdi:arrow-collapse-down",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        value_fn=lambda device: _proc_press(device.Ventilation.Fan.PressSup),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Fan is not None
        and device.Ventilation.Fan.PressSup is not None,
    ),
    DucoBoxSensorEntityDescription(
        key="pressure_eha",
        name="Pressure (Exhaust)",
        icon="mdi:arrow-collapse-up",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        value_fn=lambda device: _proc_press(device.Ventilation.Fan.PressEha),
        exists_fn=lambda device: device.Ventilation is not None
        and device.Ventilation.Fan is not None
        and device.Ventilation.Fan.PressEha is not None,
    ),
)
SENSORS_ZONES: dict[str, tuple[DucoNodeSensorEntityDescription, ...]] = {
    "BOX": (
        DucoNodeSensorEntityDescription(
            key="mode",
            name="Ventilation Mode",
            sensor_key="Mode",
            type="BOX",
            value_fn=lambda node: node.Ventilation.Mode,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.Mode is not None,
        ),
        DucoNodeSensorEntityDescription(
            key="state",
            name="Ventilation State",
            sensor_key="State",
            type="BOX",
            value_fn=lambda node: node.Ventilation.State,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.State is not None,
        ),
        DucoNodeSensorEntityDescription(
            key="flow_lvl_tgt",
            name="Flow Level Target",
            sensor_key="FlowLvlTgt",
            type="BOX",
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.Ventilation.FlowLvlTgt,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.FlowLvlTgt is not None,
        ),
        DucoNodeSensorEntityDescription(
            key="time_state_remain",
            name="Time State Remaining",
            sensor_key="TimeStateRemain",
            type="BOX",
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: node.Ventilation.TimeStateRemain,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.TimeStateRemain is not None,
        ),
        DucoNodeSensorEntityDescription(
            key="time_state_end",
            name="Time State Ending",
            sensor_key="TimeStateEnd",
            type="BOX",
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: node.Ventilation.TimeStateEnd,
            exists_fn=lambda node: node.Ventilation is not None
            and node.Ventilation.TimeStateEnd is not None,
        ),
        DucoNodeSensorEntityDescription(
            key="temp",
            name="Temperature",
            sensor_key="Temp",
            type="BOX",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: node.Sensor.Temp,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Temp is not None,
        ),
        DucoNodeSensorEntityDescription(
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
        DucoNodeSensorEntityDescription(
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
        DucoNodeSensorEntityDescription(
            key="temp",
            name="Temperature",
            sensor_key="Temp",
            type="UCCO2",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: node.Sensor.Temp,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Temp is not None,
        ),
        DucoNodeSensorEntityDescription(
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
        DucoNodeSensorEntityDescription(
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
        DucoNodeSensorEntityDescription(
            key="temp",
            name="Temperature",
            sensor_key="Temp",
            type="BSRH",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: node.Sensor.Temp,
            exists_fn=lambda node: node.Sensor is not None
            and node.Sensor.Temp is not None,
        ),
        DucoNodeSensorEntityDescription(
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
        DucoNodeSensorEntityDescription(
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


def _proc_temp(temp: float | None) -> float | None:
    return temp / 10.0 if temp is not None else None


def _proc_speed(speed: int | None) -> int | None:
    return speed if speed is not None else None


def _proc_press(press: int | None) -> int | None:
    return press if press is not None else None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DucoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

    box_data = entry.runtime_data.data.info
    box_entities: list = [
        DucoBoxSensorEntity(entry.runtime_data, description)
        for description in SENSORS_DUCOBOX
        if description.exists_fn(box_data)
    ]
    async_add_entities(box_entities)

    nodes_data = entry.runtime_data.data.nodes
    for node in nodes_data:
        key = node.General.Type
        node_entities: list = [
            DucoNodeSensorEntity(entry.runtime_data, description, node)
            for description in SENSORS_ZONES.get(key, ())
            if description.exists_fn(node)
        ]
        async_add_entities(node_entities)


class DucoBoxSensorEntity(DucoEntity, SensorEntity):
    """Representation of a Duco Sensor."""

    entity_description: DucoBoxSensorEntityDescription

    def __init__(
        self,
        coordinator: DucoDeviceUpdateCoordinator,
        description: DucoBoxSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}_{description.key}"
        if not description.enabled_fn(self.coordinator.data.info):
            self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data.info)

    @property
    def available(self) -> bool:
        """Return availability of meter."""
        return super().available and self.native_value is not None


class DucoNodeSensorEntity(DucoEntity, SensorEntity):
    """Representation of a Duco Sensor."""

    entity_description: DucoNodeSensorEntityDescription
    node: NodeDataDTO

    def __init__(
        self,
        coordinator: DucoDeviceUpdateCoordinator,
        description: DucoNodeSensorEntityDescription,
        node: NodeDataDTO,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, node)

        self.entity_description = description
        self.node = node

        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{description.key}_{node.Node}"
        )
        if not description.enabled_fn(node):
            self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return (
            self.entity_description.value_fn(self.node)
            if self.entity_description.exists_fn(self.node)
            else None
        )

    @property
    def available(self) -> bool:
        """Return availability of meter."""
        return super().available and self.native_value is not None
