from dataclasses import dataclass
from typing import Optional


@dataclass
class GeneralDTO:
    Type: str
    SubType: Optional[int]
    NetworkType: Optional[str]
    Addr: Optional[int]
    SubAddr: Optional[int]
    Parent: Optional[int]
    Asso: Optional[int]
    SwVersion: Optional[str]
    SerialBoard: Optional[str]
    UpTime: Optional[int]
    Identify: Optional[int]
    LinkMode: Optional[int]
    ProductId: Optional[int]
    SerialDuco: Optional[str]
    Name: Optional[str]


@dataclass
class NetworkDucoDTO:
    CommErrorCtr: int
    RssiRfN2M: Optional[int]
    HopRf: Optional[int]
    RssiRfN2H: Optional[int]


@dataclass
class VentilationDTO:
    State: str
    TimeStateRemain: int
    TimeStateEnd: int
    FlowLvlOvrl: int
    FlowLvlReqSensor: int
    Mode: Optional[str]
    FlowLvlTgt: Optional[int]
    Pos: Optional[int]


@dataclass
class SensorDTO:
    Temp: Optional[float]
    Co2: Optional[int]
    IaqCo2: Optional[int]
    Rh: Optional[int]
    IaqRh: Optional[int]


@dataclass
class DiagDTO:
    Errors: list[str]


@dataclass
class NodeDataDTO:
    Node: int
    General: GeneralDTO
    NetworkDuco: Optional[NetworkDucoDTO]
    Ventilation: Optional[VentilationDTO]
    Diag: Optional[DiagDTO]
    Sensor: Optional[SensorDTO]

    @property
    def id(self) -> int:
        return self.Node

    @property
    def account_module_index(self) -> str:
        return f"{self.Node}-{self.General.SerialDuco}"


@dataclass
class NodesDataDTO:
    Nodes: list[NodeDataDTO]
