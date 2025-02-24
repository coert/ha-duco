import asyncio
from typing import Any, Coroutine

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DucoConfigEntry
from .api.DTO.ActionDTO import ActionEnum
from .coordinator import DucoDeviceUpdateCoordinator
from .entity import DucoEntity


async def async_setup_entry(
    _: HomeAssistant,
    entry: DucoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    node_id = 1
    """Set up the Identify button."""
    calls: list[Coroutine[Any, Any, bool]] = []
    for node_id in entry.runtime_data.duco_nidxs:
        calls.append(entry.runtime_data.supports_update_ventilation_action(node_id))

    results = await asyncio.gather(*calls)
    for node_id, supports_update in zip(entry.runtime_data.duco_nidxs, results):
        if supports_update:
            async_add_entities(
                [
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node_id, ActionEnum.AUTO
                    ),
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node_id, ActionEnum.MAN1
                    ),
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node_id, ActionEnum.MAN2
                    ),
                    DucoUpdateVentStateButton(
                        entry.runtime_data, node_id, ActionEnum.MAN3
                    ),
                ]
            )


class DucoUpdateVentStateButton(DucoEntity, ButtonEntity):
    """Representation of a identify button."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = ButtonDeviceClass.UPDATE

    def __init__(
        self, coordinator: DucoDeviceUpdateCoordinator, node_id: int, action: ActionEnum
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_identify_{node_id}_{action.value}"
        )
        self._node_id = node_id
        self._action = action
        self._attr_name = f"Set Ventilation Mode {action.value}"

    # @duco_exception_handler
    async def async_press(self) -> None:
        """Identify the device."""
        await self.coordinator.api.set_ventilation_action(self._node_id, self._action)
