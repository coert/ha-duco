from dataclasses import dataclass
from typing import Optional


@dataclass
class BoardDTO:
    ApiVersion: Optional[str]
    ApiAccessSecurityLvl: Optional[int]
    PublicApiVersion: Optional[str]
    SwVersionComm: Optional[str]
    SwVersionCommBoot: Optional[str]
    SwVersionBox: Optional[str]
    SwVersionBoxBoot: Optional[str]
    BoxName: Optional[str]
    BoxSubType: Optional[int]
    CommSubType: Optional[int]
    BoxSubTypeName: Optional[str]
    CommSubTypeName: Optional[str]
    ProductIdBox: Optional[int]
    ProductIdComm: Optional[int]
    SerialBoardBox: Optional[str]
    SerialBoardComm: Optional[str]
    SerialDucoBox: Optional[str]
    SerialDucoComm: Optional[str]
    UpTime: Optional[int]
    Time: Optional[int]


@dataclass
class LanDTO:
    Mode: Optional[str]
    Ip: Optional[str]
    NetMask: Optional[str]
    DefaultGateway: Optional[str]
    Dns: Optional[str]
    Mac: Optional[str]
    HostName: Optional[str]
    DucoClientIp: Optional[str]
    WifiClientSsid: Optional[str]
    RssiWifi: Optional[int]
    ScanWifi: Optional[list]


@dataclass
class NetworkDucoDTO:
    HomeId: Optional[str]
    State: Optional[str]


@dataclass
class GeneralDTO:
    Board: BoardDTO
    Lan: LanDTO
    NetworkDuco: Optional[NetworkDucoDTO]


@dataclass
class SubSystemDTO:
    Component: Optional[str]
    Status: Optional[str]


@dataclass
class DiagDTO:
    Errors: Optional[list[str]]
    SubSystems: Optional[list[SubSystemDTO]]


@dataclass
class SensorDTO:
    TempOda: Optional[int]
    TempSup: Optional[int]
    TempEta: Optional[int]
    TempEha: Optional[int]


@dataclass
class FanDTO:
    SpeedSup: Optional[int]
    PressSupTgt: Optional[int]
    PressSup: Optional[int]
    PwmLvlSup: Optional[int]
    PwmSup: Optional[int]
    SpeedEha: Optional[int]
    PressEha: Optional[int]
    PressEhaTgt: Optional[int]
    PwmEha: Optional[int]
    PwmLvlEha: Optional[int]


@dataclass
class CalibrationDTO:
    Valid: Optional[bool]
    State: Optional[str]
    Status: Optional[str]
    Error: Optional[int]
    ResistSupZone1: Optional[int]
    ResistEha: Optional[int]
    PressSupCfgZone1: Optional[int]
    PressEha: Optional[int]
    PressEhaCfg: Optional[int]
    FlowEhaCfg: Optional[int]


@dataclass
class VentilationDTO:
    Sensor: SensorDTO
    Fan: Optional[FanDTO]
    Calibration: CalibrationDTO


@dataclass
class HeatRecoveryGeneralDTO:
    TimeFilterRemain: Optional[int]


@dataclass
class BypassDTO:
    Pos: Optional[int]
    TempSupTgt: Optional[int]


@dataclass
class ProtectFrostDTO:
    State: Optional[int]
    PressReduct: Optional[int]
    HeaterOdaPresent: Optional[bool]


@dataclass
class HeatRecoveryDTO:
    General: HeatRecoveryGeneralDTO
    Bypass: Optional[BypassDTO]
    ProtectFrost: Optional[ProtectFrostDTO]


@dataclass
class NightBoostGeneralDTO:
    TempOutsideAvgThs: Optional[int]
    TempOutsideAvg: Optional[int]
    TempOutside: Optional[int]
    TempComfort: Optional[int]
    TimeCond: Optional[bool]
    TempZone1: Optional[int]
    FlowLvlReqZone1: Optional[int]


@dataclass
class NightBoostDTO:
    General: NightBoostGeneralDTO


@dataclass
class VentCoolGeneralDTO:
    State: Optional[int]
    TempOutsideAvgThs: Optional[int]
    TempOutsideAvg: Optional[int]
    TempInside: Optional[int]
    TempInsideMin: Optional[int]
    TempInsideMax: Optional[int]
    TempComfort: Optional[int]
    TempOutside: Optional[int]
    Co2Cond: Optional[bool]


@dataclass
class VentCoolDTO:
    General: VentCoolGeneralDTO


@dataclass
class WeatherStationDTO:
    Type: Optional[int]


@dataclass
class WeatherStationDiagDTO:
    Enable: Optional[bool]


@dataclass
class WeatherHandlerDTO:
    WeatherStation: WeatherStationDTO
    WeatherStationDiag: WeatherStationDiagDTO


@dataclass
class AzureConnectionDTO:
    State: Optional[int]
    Id: Optional[int]
    HostName: Optional[str]
    DeviceId: Optional[str]


@dataclass
class AzureDTO:
    Connection: AzureConnectionDTO


@dataclass
class InfoDTO:
    General: GeneralDTO
    Diag: Optional[DiagDTO]
    HeatRecovery: Optional[HeatRecoveryDTO]
    Ventilation: Optional[VentilationDTO]
    NightBoost: Optional[NightBoostDTO]
    VentCool: Optional[VentCoolDTO]
    WeatherHandler: Optional[WeatherHandlerDTO]
    Azure: Optional[AzureDTO]
