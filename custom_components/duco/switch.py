from __future__ import annotations

import asyncio
import inspect
from typing import Any, Coroutine
from dataclasses import dataclass
from collections.abc import Awaitable, Callable

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DucoConfigEntry
from .api.private.duco_client import DucoClient
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .const import DeviceResponseEntry, LOGGER
from .coordinator import DucoDeviceUpdateCoordinator
from .entity import DucoEntity
from .api.utils import str_to_bool


PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class DucoSwitchEntityDescription(SwitchEntityDescription):
    """Class describing HomeWizard switch entities."""

    action_state: str
    available_fn: Callable[[DeviceResponseEntry, int, str], bool]
    is_on_fn: Callable[[DeviceResponseEntry], bool | None]
    set_fn: Callable[[DeviceResponseEntry, DucoClient, int, str, bool], Awaitable[None]]


SWITCHES = [
    DucoSwitchEntityDescription(
        key="identify",
        name="Identify",
        action_state="SetIdentify",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        available_fn=lambda x, nidx, node_action: nidx in x.node_actions
        and any(
            action.Action == node_action
            for action in x.node_actions[nidx].Actions
            if action.Action == node_action
        ),
        is_on_fn=lambda x: str_to_bool(x.action_state),
        set_fn=lambda x, api, nidx, node_action, value: x.set_node_action_state(
            api, nidx, node_action, value
        ),
    ),
]


async def async_setup_entry(
    _: HomeAssistant,
    entry: DucoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug(f"button:{inspect.currentframe().f_code.co_name}")

    """Set up the Identify button."""
    calls_nodes: list[Coroutine[Any, Any, NodeDataDTO | None]] = []
    for node_id in entry.runtime_data.duco_nidxs:
        calls_nodes.append(entry.runtime_data.api.get_node_info(node_id))
    node_results = await asyncio.gather(*calls_nodes)

    add_entities: list[DucoSwitchEntity] = [
        DucoSwitchEntity(entry.runtime_data, node, switch)
        for node in node_results
        if node is not None
        for switch in SWITCHES
    ]

    async_add_entities(add_entities)


class DucoSwitchEntity(DucoEntity, SwitchEntity):
    """Representation of a HomeWizard switch."""

    entity_description: DucoSwitchEntityDescription

    def __init__(
        self,
        coordinator: DucoDeviceUpdateCoordinator,
        node: NodeDataDTO,
        description: DucoSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, node)

        self._node_id = node.Node
        self._action_state = description.action_state
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{self._node_id}_{description.key}"
        )
        self.entity_id = f"switch.{node.General.Type}_{description.key}"

        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self.entity_description.available_fn(
            self.coordinator.data, self._node_id, self._action_state
        )

    @property
    def is_on(self) -> bool | None:
        """Return state of the switch."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.set_fn(
            self.coordinator.data,
            self.coordinator.api,
            self._node_id,
            self.entity_description.action_state,
            True,
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.set_fn(
            self.coordinator.data,
            self.coordinator.api,
            self._node_id,
            self.entity_description.action_state,
            False,
        )
        await self.coordinator.async_refresh()
