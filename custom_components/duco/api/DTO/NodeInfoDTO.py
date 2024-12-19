from dataclasses import dataclass
from typing import Optional


@dataclass
class GeneralDTO:
    Type: str
    SubType: int
    NetworkType: str
    Addr: int
    SubAddr: int
    Parent: int
    Asso: int
    SwVersion: str
    SerialBoard: str
    UpTime: int
    Identify: int
    LinkMode: int
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


@dataclass
class DiagDTO:
    Errors: list[str]


@dataclass
class NodeDataDTO:
    Node: int
    General: GeneralDTO
    NetworkDuco: NetworkDucoDTO
    Ventilation: VentilationDTO
    Diag: DiagDTO
    Sensor: Optional[SensorDTO]


@dataclass
class NodesDataDTO:
    Nodes: list[NodeDataDTO]
