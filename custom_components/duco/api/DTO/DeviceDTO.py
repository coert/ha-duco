from dataclasses import dataclass

from .InfoDTO import BoardDTO, LanDTO, VentilationDTO
from .NodeInfoDTO import NodeDataDTO


@dataclass
class DeviceDTO:
    id: int
    account_module_index: str
    name: str
    type: str
    box_irbd: str
    box_index: int
    box_serial_number: str
    box_service_number: str
    nodes: list[NodeDataDTO]
    board: BoardDTO | None = None
    lan: LanDTO | None = None
    ventilation: VentilationDTO | None = None
