from __future__ import annotations

from typing import Any, TYPE_CHECKING
import logging
from dataclasses import dataclass, field
from datetime import timedelta

from homeassistant.const import Platform

from .api.DTO.InfoDTO import InfoDTO
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .api.DTO.ActionDTO import NodeActionDTO as ActionDTO
from .api.DTO.NodeActionDTO import NodeActionsDTO

if TYPE_CHECKING:
    from .api.private.duco_client import DucoClient

DOMAIN = "duco"
MANUFACTURER = "Duco"
PLATFORMS = [Platform.BUTTON, Platform.SENSOR, Platform.SWITCH]
API_LOCAL_IP = "192.168.5.4"
API_PRIVATE_URL = f"https://{API_LOCAL_IP}"
API_PUBLIC_URL = "https://vd-dev-weu-apim.azure-api.net/publicapi"

LOGGER = logging.getLogger(__package__)

# Time between data updates
UPDATE_INTERVAL = timedelta(seconds=180)


@dataclass
class DeviceResponseEntry:
    """Dict describing a single response entry."""

    _action_state: Any | None = None

    info: InfoDTO | None = None
    nodes: dict[int, NodeDataDTO] = field(default_factory=dict)
    actions: ActionDTO | None = None
    node_actions: dict[int, NodeActionsDTO] = field(default_factory=dict)

    @property
    def action_state(self) -> str | None:
        return self._action_state

    async def set_node_action_state(
        self, api: DucoClient, nidx: int, node_action: str, value: Any
    ):
        self._action_state = value
        await api.set_node_action_state(nidx, node_action, value)
