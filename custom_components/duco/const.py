from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from .api.DTO.InfoDTO import InfoDTO
from .api.DTO.NodeInfoDTO import NodeDataDTO

DOMAIN = "duco"
MANUFACTURER = "Duco"
PLATFORMS = ["sensor"]
API_LOCAL_IP = "192.168.5.4"
API_PRIVATE_URL = f"https://{API_LOCAL_IP}"
API_PUBLIC_URL = "https://vd-dev-weu-apim.azure-api.net/publicapi"

LOGGER = logging.getLogger(__package__)

# Time between data updates
UPDATE_INTERVAL = timedelta(seconds=60)


@dataclass
class DeviceResponseEntry:
    """Dict describing a single response entry."""

    info: InfoDTO
    nodes: list[NodeDataDTO]
