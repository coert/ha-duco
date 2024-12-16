from dataclasses import dataclass


@dataclass
class BoardDTO:
    ApiVersion: str
    ApiAccessSecurityLvl: int
    PublicApiVersion: str
    SwVersionComm: str
    SwVersionCommBoot: str
    SwVersionBox: str
    SwVersionBoxBoot: str
    BoxName: str
    BoxSubType: int
    CommSubType: int
    BoxSubTypeName: str
    CommSubTypeName: str
    ProductIdBox: int
    ProductIdComm: int
    SerialBoardBox: str
    SerialBoardComm: str
    SerialDucoBox: str
    SerialDucoComm: str
    UpTime: int
    Time: int


@dataclass
class LanDTO:
    Mode: str
    Ip: str
    NetMask: str
    DefaultGateway: str
    Dns: str
    Mac: str
    HostName: str
    DucoClientIp: str
    WifiClientSsid: str
    RssiWifi: int
    ScanWifi: list


@dataclass
class NetworkDucoDTO:
    HomeId: str
    State: str


@dataclass
class GeneralDTO:
    Board: BoardDTO
    Lan: LanDTO
    NetworkDuco: NetworkDucoDTO


@dataclass
class SubSystemDTO:
    Component: str
    Status: str


@dataclass
class DiagDTO:
    Errors: list
    SubSystems: list[SubSystemDTO]


@dataclass
class SensorDTO:
    TempOda: int
    TempSup: int
    TempEta: int
    TempEha: int


@dataclass
class FanDTO:
    SpeedSup: int
    PressSupTgt: int
    PressSup: int
    PwmLvlSup: int
    PwmSup: int
    SpeedEha: int
    PressEha: int
    PressEhaTgt: int
    PwmEha: int
    PwmLvlEha: int


@dataclass
class CalibrationDTO:
    Valid: bool
    State: str
    Status: str
    Error: int
    ResistSupZone1: int
    ResistEha: int
    PressSupCfgZone1: int
    PressEha: int
    PressEhaCfg: int
    FlowEhaCfg: int


@dataclass
class VentilationDTO:
    Sensor: SensorDTO
    Fan: FanDTO
    Calibration: CalibrationDTO


@dataclass
class HeatRecoveryGeneralDTO:
    TimeFilterRemain: int


@dataclass
class BypassDTO:
    Pos: int
    TempSupTgt: int


@dataclass
class ProtectFrostDTO:
    State: int
    PressReduct: int
    HeaterOdaPresent: bool


@dataclass
class HeatRecoveryDTO:
    General: HeatRecoveryGeneralDTO
    Bypass: BypassDTO
    ProtectFrost: ProtectFrostDTO


@dataclass
class NightBoostGeneralDTO:
    TempOutsideAvgThs: int
    TempOutsideAvg: int
    TempOutside: int
    TempComfort: int
    TimeCond: bool
    TempZone1: int
    FlowLvlReqZone1: int


@dataclass
class NightBoostDTO:
    General: NightBoostGeneralDTO


@dataclass
class VentCoolGeneralDTO:
    State: int
    TempOutsideAvgThs: int
    TempOutsideAvg: int
    TempInside: int
    TempInsideMin: int
    TempInsideMax: int
    TempComfort: int
    TempOutside: int
    Co2Cond: bool


@dataclass
class VentCoolDTO:
    General: VentCoolGeneralDTO


@dataclass
class WeatherStationDTO:
    Type: int


@dataclass
class WeatherStationDiagDTO:
    Enable: bool


@dataclass
class WeatherHandlerDTO:
    WeatherStation: WeatherStationDTO
    WeatherStationDiag: WeatherStationDiagDTO


@dataclass
class AzureConnectionDTO:
    State: int
    Id: int
    HostName: str
    DeviceId: str


@dataclass
class AzureDTO:
    Connection: AzureConnectionDTO


@dataclass
class InfoDTO:
    General: GeneralDTO
    Diag: DiagDTO | None = None
    HeatRecovery: HeatRecoveryDTO | None = None
    Ventilation: VentilationDTO | None = None
    NightBoost: NightBoostDTO | None = None
    VentCool: VentCoolDTO | None = None
    WeatherHandler: WeatherHandlerDTO | None = None
    Azure: AzureDTO | None = None
