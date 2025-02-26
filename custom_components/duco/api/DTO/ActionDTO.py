from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ActionEnum(Enum):
    AUTO = "AUTO"
    AUT1 = "AUT1"
    AUT2 = "AUT2"
    AUT3 = "AUT3"
    MAN1 = "MAN1"
    MAN2 = "MAN2"
    MAN3 = "MAN3"
    EMPT = "EMPT"
    CNT1 = "CNT1"
    CNT2 = "CNT2"
    CNT3 = "CNT3"
    MAN1x2 = "MAN1x2"
    MAN2x2 = "MAN2x2"
    MAN3x2 = "MAN3x2"
    MAN1x3 = "MAN1x3"
    MAN2x3 = "MAN2x3"
    MAN3x3 = "MAN3x3"


@dataclass
class NodeActionDTO:
    Action: str
    ValType: str
    Enum: Optional[List[str]] = field(default_factory=list)


@dataclass
class NodeActionTriggerDTO:
    Action: str


@dataclass
class NodeActionSetDTO:
    Action: str
    Val: str


# supported_actions = [
#     {"Action": "SetTime", "ValType": "Integer"},
#     {
#         "Action": "SetNetworkDucoState",
#         "ValType": "Enum",
#         "Enum": ["OPERATIONAL", "INSTALL"],
#     },
#     {
#         "Action": "SetVentilationCalibrationState",
#         "ValType": "Enum",
#         "Enum": ["STOP", "CONFIG_MAX", "START", "VERIFY_LOW", "VERIFY_HIGH"],
#     },
#     {
#         "Action": "SetVentilationCalibrationSubState",
#         "ValType": "Enum",
#         "Enum": [
#             "IDLE",
#             "SUPPLY_ZONE_1",
#             "SUPPLY_ZONE_2",
#             "EXTRACT",
#             "SUPPLY_ZONE_3",
#             "SUPPLY_ZONE_4",
#             "SUPPLY_ZONE_5",
#             "SUPPLY_ZONE_6",
#             "SUPPLY_ZONE_7",
#             "SUPPLY_ZONE_8",
#             "ALL_OPEN",
#             "FIND_CALIB_DATA",
#             "BASE_NF",
#             "PEAK_NF",
#         ],
#     },
#     {"Action": "ResetNetworkDuco", "ValType": "None"},
#     {"Action": "UpdateFirmware", "ValType": "None"},
#     {"Action": "DownloadFirmware", "ValType": "String"},
#     {"Action": "DownloadAndUpdateFirmware", "ValType": "String"},
#     {"Action": "SetIdentify", "ValType": "Boolean"},
#     {"Action": "SetIdentifyAll", "ValType": "Boolean"},
#     {"Action": "RebootBox", "ValType": "None"},
#     {"Action": "RebootComm", "ValType": "None"},
#     {"Action": "ReconnectWifi", "ValType": "None"},
#     {"Action": "ScanWifi", "ValType": "None"},
#     {"Action": "SetWifiApMode", "ValType": "Boolean"},
#     {"Action": "SetWifiApKey", "ValType": "String"},
#     {"Action": "SetSerialDucoBox", "ValType": "String"},
#     {"Action": "SetSerialDucoComm", "ValType": "String"},
#     {"Action": "UpdateNodeData", "ValType": "None"},
#     {"Action": "EnterUnlockCode", "ValType": "Integer"},
#     {"Action": "ClearNodeNames", "ValType": "None"},
#     {"Action": "ResetFilterTimeRemain", "ValType": "None"},
#     {"Action": "EnterVentilationCalibrationCode", "ValType": "Integer"},
#     {"Action": "TriggerWeatherStationComm", "ValType": "None"},
#     {"Action": "ResetWeatherStationComm", "ValType": "None"},
#     {"Action": "SetAzureConnectionString1", "ValType": "String"},
#     {"Action": "SetAzureConnectionString2", "ValType": "String"},
#     {"Action": "StartAzureConnection", "ValType": "None"},
#     {"Action": "StopAzureConnection", "ValType": "None"},
#     {"Action": "RestartAzureConnection", "ValType": "None"},
#     {"Action": "SetBoxSubType", "ValType": "Integer"},
#     {"Action": "SetCommSubType", "ValType": "Integer"},
#     {"Action": "UnlockDevelopmentApi", "ValType": "Integer"},
# ]
