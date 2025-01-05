"""Base entity for the HomeWizard integration."""

from __future__ import annotations

from homeassistant.const import ATTR_CONNECTIONS, ATTR_IDENTIFIERS
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    CONNECTION_UPNP,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .coordinator import DucoDeviceUpdateCoordinator


class DucoEntity(CoordinatorEntity[DucoDeviceUpdateCoordinator]):
    """Defines a Duco entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: DucoDeviceUpdateCoordinator, node: NodeDataDTO | None = None
    ) -> None:
        """Initialize the Duco entity."""
        super().__init__(coordinator)

        if node is not None:
            self._attr_device_info = DeviceInfo(
                manufacturer=MANUFACTURER,
                name=f"{MANUFACTURER} {node.General.Type}",
                sw_version=node.General.SwVersion,
                model_id=str(node.General.ProductId),
                model=f"{node.General.Type}",
            )

            if (
                serial_number := node.NetworkDuco.HopRf or node.General.SerialBoard
            ) is not None:
                if node.NetworkDuco.HopRf:
                    self._attr_device_info[ATTR_CONNECTIONS] = {
                        (CONNECTION_UPNP, f"{serial_number}")
                    }
                self._attr_device_info[ATTR_IDENTIFIERS] = {
                    (DOMAIN, f"{serial_number}")
                }

        else:
            brand_name = f"{coordinator.data.info.General.Board.BoxName.capitalize()} "
            box_sub_type_name = str(coordinator.data.info.General.Board.BoxSubTypeName)
            brand_name += " ".join(
                [word.capitalize() for word in box_sub_type_name.split("_")]
            )
            self._attr_device_info = DeviceInfo(
                manufacturer=MANUFACTURER,
                name=f"{MANUFACTURER}Box",
                sw_version=coordinator.data.info.General.Board.SwVersionBox,
                model_id=str(coordinator.data.info.General.Board.ProductIdBox),
                model=brand_name,
            )

            if (serial_number := coordinator.data.info.General.Lan.Mac) is not None:
                self._attr_device_info[ATTR_CONNECTIONS] = {
                    (CONNECTION_NETWORK_MAC, serial_number)
                }
                self._attr_device_info[ATTR_IDENTIFIERS] = {(DOMAIN, serial_number)}
