from dataclasses import dataclass
from typing import Optional

from .InfoDTO import InfoDTO
from .NodeInfoDTO import NodeDataDTO


@dataclass
class DeviceDTO:
    id: int
    account_module_index: str
    name: str
    type: str
    box_irbd: Optional[str]
    box_index: Optional[int]
    box_serial_number: Optional[str]
    box_service_number: Optional[str]
    info: InfoDTO
    nodes: list[NodeDataDTO]
