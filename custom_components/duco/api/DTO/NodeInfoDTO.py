from dataclasses import dataclass


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
    ProductId: int | None = None
    SerialDuco: str | None = None
    Name: str | None = None


@dataclass
class NetworkDucoDTO:
    CommErrorCtr: int
    RssiRfN2M: int | None = None
    HopRf: int | None = None
    RssiRfN2H: int | None = None


@dataclass
class VentilationDTO:
    State: str
    TimeStateRemain: int
    TimeStateEnd: int
    FlowLvlOvrl: int
    FlowLvlReqSensor: int
    Mode: str | None = None
    FlowLvlTgt: int | None = None
    Pos: int | None = None


@dataclass
class SensorDTO:
    Temp: float | None = None
    Co2: int | None = None
    IaqCo2: int | None = None


@dataclass
class DiagDTO:
    Errors: list


@dataclass
class NodeDataDTO:
    Node: int
    General: GeneralDTO
    NetworkDuco: NetworkDucoDTO
    Ventilation: VentilationDTO
    Diag: DiagDTO
    Sensor: SensorDTO | None = None


@dataclass
class NodesDataDTO:
    Nodes: list[NodeDataDTO]
