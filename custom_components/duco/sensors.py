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
    REVOLUTIONS_PER_MINUTE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api.DTO.DeviceDTO import DeviceDTO
from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class DucoSensorEntityDescription(SensorEntityDescription):
    """Describes an Duco sensor entity."""

    key: str
    name: str
    exists_fn: Callable[[Any], bool] = lambda _: True
    value_fn: Callable[[Any], SensorEntityDescription]


# Define the sensor types
SENSORS_WTW: tuple[DucoSensorEntityDescription, ...] = (
    DucoSensorEntityDescription(
        key="fan_speed_sup",
        name="Fan Speed Supply",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        value_fn=lambda device: device.ventilation.Fan.SpeedSup,
        exists_fn=lambda device: device.ventilation is not None
        and device.ventilation.Fan is not None
        and device.ventilation.Fan.SpeedSup is not None,
    ),
)
SENSORS_ZONES: tuple[DucoSensorEntityDescription, ...] = ()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
    """Set up Duco sensor based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Ensure the coordinator has refreshed its data
    await coordinator.async_config_entry_first_refresh()

    devices = coordinator.data

    list_device_dto_heat_pump: list[DeviceDTO] = []
    list_device_dto_zones_controllers: list[DeviceDTO] = []

    for device in devices:
        if isinstance(device, dict):
            device = from_dict(data_class=DeviceDTO, data=device)
        assert isinstance(device, DeviceDTO), f"Expected DeviceDTO, got {type(device)}"
        if device.type == "heat_pump":
            list_device_dto_heat_pump.append(device)
        elif device.type == "zones_controller":
            list_device_dto_zones_controllers.append(device)

    async_add_entities(
        DucoSensorEntity(coordinator, device, description)
        for device in list_device_dto_heat_pump
        for description in SENSORS_WTW
        if description.exists_fn(device)
    )

    async_add_entities(
        DucoSensorEntity(coordinator, device, description)
        for device in list_device_dto_heat_pump
        for description in SENSORS_ZONES
        if description.exists_fn(device)
    )


class DucoSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an Duco sensor."""

    device: DeviceDTO
    entity_description: DucoSensorEntityDescription

    def __init__(
        self,
        coordinator,
        device: DeviceDTO,
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
        for updated_device in self.coordinator.data.values():
            if isinstance(updated_device, dict):
                updated_device = from_dict(data_class=DeviceDTO, data=updated_device)
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
