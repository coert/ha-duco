from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any, Coroutine
from dataclasses import dataclass
from collections.abc import Awaitable, Callable

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DucoConfigEntry
from .api.private.duco_client import DucoClient
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .api.DTO.ActionDTO import ActionEnum
from .const import DeviceResponseEntry
from .coordinator import DucoDeviceUpdateCoordinator
from .entity import DucoEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


@dataclass(frozen=True, kw_only=True)
class DucoButtonEntityDescription(ButtonEntityDescription):
    """Class describing Duco button entities."""

    available_fn: Callable[[DeviceResponseEntry, int, str], bool]
    set_fn: Callable[[DucoClient, int, str], Awaitable[None]]


BUTTONS = [
    DucoButtonEntityDescription(
        key="fan_state_auto",
        name="Fan speed auto",
        device_class=ButtonDeviceClass.UPDATE,
        icon="mdi:fan-auto",
        available_fn=lambda x, nidx, node_action: nidx in x.node_actions
        and any(
            action_enum == ActionEnum.AUTO.value
            for action in x.node_actions[nidx].Actions
            if action.Action == node_action and action.Enum is not None
            for action_enum in action.Enum
        ),
        set_fn=lambda api, nidx, node_action: api.set_node_action_state(
            nidx, node_action, ActionEnum.AUTO
        ),
    ),
    DucoButtonEntityDescription(
        key="fan_state_man1",
        name="Fan speed 1",
        device_class=ButtonDeviceClass.UPDATE,
        icon="mdi:fan-speed-1",
        available_fn=lambda x, nidx, node_action: nidx in x.node_actions
        and any(
            action_enum == ActionEnum.MAN1.value
            for action in x.node_actions[nidx].Actions
            if action.Action == node_action and action.Enum is not None
            for action_enum in action.Enum
        ),
        set_fn=lambda api, nidx, node_action: api.set_node_action_state(
            nidx, node_action, ActionEnum.MAN1
        ),
    ),
    DucoButtonEntityDescription(
        key="fan_state_man2",
        name="Fan speed 2",
        device_class=ButtonDeviceClass.UPDATE,
        icon="mdi:fan-speed-2",
        available_fn=lambda x, nidx, node_action: nidx in x.node_actions
        and any(
            action_enum == ActionEnum.MAN2.value
            for action in x.node_actions[nidx].Actions
            if action.Action == node_action and action.Enum is not None
            for action_enum in action.Enum
        ),
        set_fn=lambda api, nidx, node_action: api.set_node_action_state(
            nidx, node_action, ActionEnum.MAN2
        ),
    ),
    DucoButtonEntityDescription(
        key="fan_state_man3",
        name="Fan speed 3",
        device_class=ButtonDeviceClass.UPDATE,
        icon="mdi:fan-speed-3",
        available_fn=lambda x, nidx, node_action: nidx in x.node_actions
        and any(
            action_enum == ActionEnum.MAN3.value
            for action in x.node_actions[nidx].Actions
            if action.Action == node_action and action.Enum is not None
            for action_enum in action.Enum
        ),
        set_fn=lambda api, nidx, node_action: api.set_node_action_state(
            nidx, node_action, ActionEnum.MAN3
        ),
    ),
]


async def async_setup_entry(
    _: HomeAssistant,
    entry: DucoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug(f"button:{inspect.currentframe().f_code.co_name}")

    """Set up the Identify button."""
    calls_nodes: list[Coroutine[Any, Any, NodeDataDTO | None]] = []
    for node_id in entry.runtime_data.duco_nidxs:
        calls_nodes.append(entry.runtime_data.api.get_node_info(node_id))
    node_results = await asyncio.gather(*calls_nodes)

    add_entities: list[DucoVentActionButtonEntity] = [
        DucoVentActionButtonEntity(entry.runtime_data, node, button)
        for node in node_results
        if node is not None
        for button in BUTTONS
    ]

    async_add_entities(add_entities)


class DucoVentActionButtonEntity(DucoEntity, ButtonEntity):
    """Representation of a ventilation action button."""

    entity_description: DucoButtonEntityDescription

    def __init__(
        self,
        coordinator: DucoDeviceUpdateCoordinator,
        node: NodeDataDTO,
        description: DucoButtonEntityDescription,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator, node)

        self._node_id = node.Node
        self._action_state = "SetVentilationState"
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{self._node_id}_{description.key}"
        )
        self.entity_id = f"button.{node.General.Type}_{description.key}"

        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self.entity_description.available_fn(
            self.coordinator.data, self._node_id, self._action_state
        )

    async def async_press(self) -> None:
        """Activate the ventilation action."""
        await self.entity_description.set_fn(
            self.coordinator.api, self._node_id, self._action_state
        )
        await self.coordinator.async_refresh()
