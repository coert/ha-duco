from __future__ import annotations

import inspect
from dataclasses import dataclass
from collections.abc import Awaitable, Callable

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DucoConfigEntry
from .api.private.duco_client import DucoClient
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .api.DTO.NodeConfigDTO import ValRange
from .const import DeviceResponseEntry, LOGGER
from .coordinator import DucoDeviceUpdateCoordinator
from .entity import DucoEntity


@dataclass(frozen=True, kw_only=True)
class DucoNumberEntityDescription(NumberEntityDescription):
    """Class describing Duco button entities."""

    node_config: str
    exists_fn: Callable[[DeviceResponseEntry, int, str], bool] = lambda x, y, z: True
    available_fn: Callable[[DeviceResponseEntry, int, str], bool] = lambda x, y, z: True
    set_fn: Callable[[DucoClient, int, str, int], Awaitable[None]]


NUMBERS = [
    DucoNumberEntityDescription(
        node_config="FlowLvlAutoMin",
        key="flow_lvl_auto_min",
        name="Fan AUTO min",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="FlowLvlAutoMax",
        key="flow_lvl_auto_max",
        name="Fan AUTO max",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="FlowMax",
        key="flow_max",
        name="Flow max",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="FlowLvlMan1",
        key="flow_lvl_man1",
        name="Fan MAN1",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="FlowLvlMan2",
        key="flow_lvl_man2",
        name="Fan MAN2",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="FlowLvlMan3",
        key="flow_lvl_man3",
        name="Fan MAN3",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=PERCENTAGE,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="TimeMan",
        key="time_man",
        name="Man duration",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="UcErrorMode",
        key="uc_error_mode",
        name="UC error mode",
        entity_category=EntityCategory.CONFIG,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="Co2SetPoint",
        key="co2_set_point",
        name="CO₂ Set Point",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="TempDepEnable",
        key="temp_dep_enable",
        name="Temperature dependency enable",
        entity_category=EntityCategory.CONFIG,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
    DucoNumberEntityDescription(
        node_config="ShowSensorLvl",
        key="show_sensor_lvl",
        name="Show sensor level",
        entity_category=EntityCategory.CONFIG,
        exists_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        available_fn=lambda x, nidx, node_config: (
            nidx in x.node_configs
            and hasattr(x.node_configs[nidx], node_config)
            and getattr(x.node_configs[nidx], node_config) is not None
        ),
        set_fn=lambda api, nidx, node_config, value: api.set_node_config_value(
            nidx, node_config, value
        ),
    ),
]


async def async_setup_entry(
    _: HomeAssistant,
    entry: DucoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug(f"number:{inspect.currentframe().f_code.co_name}")

    """Set up the Identify button."""
    add_entities: list[DucoNumberEntity] = [
        DucoNumberEntity(entry.runtime_data, node, number)
        for node in entry.runtime_data.data.nodes.values()
        for number in NUMBERS
        if number.exists_fn(entry.runtime_data.data, node.Node, number.node_config)
    ]

    async_add_entities(add_entities)


class DucoNumberEntity(DucoEntity, NumberEntity):
    entity_description: DucoNumberEntityDescription

    def __init__(
        self,
        coordinator: DucoDeviceUpdateCoordinator,
        node: NodeDataDTO,
        description: DucoNumberEntityDescription,
    ) -> None:
        """Initialize number."""
        super().__init__(coordinator, node)

        self._node_id = node.Node
        self._node_config = description.node_config
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{self._node_id}_{description.key}"
        )
        self.entity_id = f"number.{node.General.Type}_{description.key}"
        self.entity_description = description

        self._attr_mode = NumberMode.SLIDER

        if self.available:
            config_attr: ValRange = getattr(
                coordinator.data.node_configs[self._node_id],
                self._node_config,
            )
            self._attr_native_min_value = config_attr.Min
            self._attr_native_max_value = config_attr.Max
            self._attr_native_step = config_attr.Inc
            self._attr_native_value = config_attr.Val

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self.entity_description.available_fn(
            self.coordinator.data, self._node_id, self._node_config
        )

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if (
            not self.coordinator.data.node_configs
            or self._node_id not in self.coordinator.data.node_configs
            or not hasattr(
                self.coordinator.data.node_configs[self._node_id], self._node_config
            )
            or (
                getattr(
                    self.coordinator.data.node_configs[self._node_id], self._node_config
                )
                is None
            )
            or (
                value := getattr(
                    self.coordinator.data.node_configs[self._node_id], self._node_config
                ).Val
            )
            is None
        ):
            return None

        return round(value)

    async def async_set_native_value(self, value: float) -> None:
        """Activate the ventilation action."""
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        await self.entity_description.set_fn(
            self.coordinator.api, self._node_id, self._node_config, int(value)
        )
        await self.coordinator.async_refresh()

        node_config: ValRange | None = getattr(
            self.coordinator.data.node_configs[self._node_id], self._node_config
        )
        if node_config is not None:
            setattr(
                self.coordinator.data.node_configs[self._node_id],
                self._node_config,
                ValRange(
                    Val=int(value),
                    Inc=node_config.Inc,
                    Min=node_config.Min,
                    Max=node_config.Max,
                ),
            )
