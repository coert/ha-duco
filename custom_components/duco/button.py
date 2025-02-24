import asyncio
import inspect
import logging
from typing import Any, Coroutine

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DucoConfigEntry
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .api.DTO.ActionDTO import ActionEnum
from .coordinator import DucoDeviceUpdateCoordinator
from .entity import DucoEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DucoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug(f"button:{inspect.currentframe().f_code.co_name}")

    """Set up the Identify button."""
    calls_nodes: list[Coroutine[Any, Any, NodeDataDTO | None]] = []
    for node_id in entry.runtime_data.duco_nidxs:
        calls_nodes.append(entry.runtime_data.api.get_node_info(node_id))
    node_results = await asyncio.gather(*calls_nodes)

    calls: list[Coroutine[Any, Any, bool]] = []
    for node_id in entry.runtime_data.duco_nidxs:
        calls.append(entry.runtime_data.supports_update_ventilation_action(node_id))

    results = await asyncio.gather(*calls)

    button_entities = []
    for node_id, supports_update in zip(entry.runtime_data.duco_nidxs, results):
        node = next(
            (
                node
                for node in node_results
                if node is not None and node.Node == node_id
            ),
            None,
        )
        assert node is not None
        if supports_update:
            button_entities.extend(
                [
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node, ActionEnum.AUTO
                    ),
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node, ActionEnum.MAN1
                    ),
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node, ActionEnum.MAN2
                    ),
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node, ActionEnum.MAN3
                    ),
                ]
            )

    async_add_entities(button_entities)


class DucoUpdateVentStateButton(DucoEntity, ButtonEntity):
    """Representation of a identify button."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = ButtonDeviceClass.UPDATE

    def __init__(
        self,
        coordinator: DucoDeviceUpdateCoordinator,
        node: NodeDataDTO,
        action: ActionEnum,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator, node)

        node_id = node.Node
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{action.value}_{node.Node}"
        )
        self._node_id = node_id
        self._action = action
        self._attr_name = f"Ventilation Mode {action.value}"

    # @duco_exception_handler
    async def async_press(self) -> None:
        """Identify the device."""
        await self.coordinator.api.set_ventilation_action(self._node_id, self._action)
