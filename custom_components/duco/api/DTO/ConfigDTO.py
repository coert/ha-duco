from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfigDTO:
    General: dict[str, dict[str, dict[str, int | str]]]
    Ventilation: dict[str, dict[str, dict[str, int]]]
    HeatRecovery: dict[str, dict[str, dict[str, int]]]
    VentCool: dict[str, dict[str, dict[str, int]]]
    NightBoost: dict[str, dict[str, dict[str, int]]]
    WeatherHandler: dict[str, dict[str, dict[str, int]]]
    Firmware: dict[str, dict[str, dict[str, int]]]
    Azure: dict[str, dict[str, dict[str, int]]]


# config_dto = {
#     "General": {
#         "Time": {
#             "TimeZone": {"Val": 1, "Min": -11, "Inc": 1, "Max": 12},
#             "Dst": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "NtpServer": {"Val": "pool.ntp.org"},
#         },
#         "Setup": {
#             "Complete": {"Val": 1, "Min": 1, "Inc": 1, "Max": 1},
#             "Language": {"Val": 1, "Min": 0, "Inc": 1, "Max": 3},
#             "Country": {"Val": 1, "Min": 1, "Inc": 1, "Max": 1},
#             "DisplayOrientation": {"Val": 210, "Min": 0, "Inc": 1, "Max": 1},
#         },
#         "Modbus": {
#             "Addr": {"Val": 1, "Min": 1, "Inc": 1, "Max": 254},
#             "Offset": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "DailyWriteReqCnt": {"Val": 100, "Min": 0, "Inc": 1, "Max": 10000},
#         },
#         "Lan": {
#             "Mode": {"Val": 1, "Min": 0, "Inc": 1, "Max": 4},
#             "Dhcp": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "MqttBroker": {"Val": "0.0.0.0"},
#             "StaticIp": {"Val": "0.0.0.0"},
#             "StaticNetMask": {"Val": "0.0.0.0"},
#             "StaticDefaultGateway": {"Val": "0.0.0.0"},
#             "StaticDns": {"Val": "8.8.8.8"},
#             "WifiClientSsid": {"Val": "Bijenmeent85_IOT"},
#             "WifiClientKey": {"Val": ""},
#             "DucoClientIp": {"Val": "0.0.0.0"},
#             "TimeDucoClientIp": {"Val": 600, "Min": 0, "Inc": 1, "Max": 3600},
#         },
#         "NodeData": {"UpdateRate": {"Val": 60, "Min": 5, "Inc": 1, "Max": 3600}},
#         "AutoRebootComm": {
#             "Period": {"Val": 7, "Min": 0, "Inc": 1, "Max": 365},
#             "Time": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1439},
#         },
#     },
#     "Ventilation": {
#         "Ctrl": {
#             "TreeBalanceThs": {"Val": 0, "Min": 0, "Inc": 1, "Max": 100},
#             "TempDepEnable": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "TempDepThsLow": {"Val": 160, "Min": 100, "Inc": 1, "Max": 240},
#             "TempDepThsHigh": {"Val": 240, "Min": 160, "Inc": 1, "Max": 350},
#         },
#         "Calibration": {
#             "GroundBound": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "PressSupCfgZone1": {"Val": 80, "Min": 0, "Inc": 1, "Max": 999},
#             "PressEhaCfg": {"Val": 48, "Min": 0, "Inc": 1, "Max": 999},
#             "FlowEhaCfg": {"Val": 325, "Min": 0, "Inc": 5, "Max": 325},
#         },
#     },
#     "HeatRecovery": {
#         "Bypass": {
#             "Mode": {"Val": 0, "Min": 0, "Inc": 1, "Max": 2},
#             "Adaptive": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "TempSupTgtZone1": {"Val": 210, "Min": 100, "Inc": 1, "Max": 255},
#             "TimeFilter": {"Val": 180, "Min": 90, "Inc": 90, "Max": 360},
#         },
#         "ProtectFrost": {
#             "PassiveHouse": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "HeaterOdaExtPresent": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#         },
#     },
#     "VentCool": {
#         "General": {
#             "Mode": {"Val": 0, "Min": 0, "Inc": 1, "Max": 2},
#             "EnableMonday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "EnableTuesday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "EnableWednesday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "EnableThursday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "EnableFriday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "EnableSaturday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "EnableSunday": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1},
#             "TimeStart": {"Val": 1320, "Min": 0, "Inc": 1, "Max": 1439},
#             "TimeStop": {"Val": 360, "Min": 0, "Inc": 1, "Max": 1439},
#             "SpeedWindMax": {"Val": 110, "Min": 0, "Inc": 1, "Max": 200},
#         }
#     },
#     "NightBoost": {
#         "General": {
#             "Enable": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#             "TempStart": {"Val": 24, "Min": 0, "Inc": 1, "Max": 60},
#             "MonthStart": {"Val": 4, "Min": 1, "Inc": 1, "Max": 12},
#             "MonthStop": {"Val": 9, "Min": 1, "Inc": 1, "Max": 12},
#             "TimeStart": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1439},
#             "TimeStop": {"Val": 1439, "Min": 0, "Inc": 1, "Max": 1439},
#             "FlowLvlReqMax": {"Val": 100, "Min": 10, "Inc": 5, "Max": 100},
#         }
#     },
#     "WeatherHandler": {
#         "WeatherStationDiag": {
#             "Type": {"Val": 0, "Min": 0, "Inc": 1, "Max": 3},
#             "Period": {"Val": 120, "Min": 10, "Inc": 5, "Max": 1200},
#             "PeriodRecovery": {"Val": 60, "Min": 10, "Inc": 5, "Max": 600},
#             "PeriodError": {"Val": 300, "Min": 10, "Inc": 5, "Max": 18000},
#             "CommErrorCount": {"Val": 3, "Min": 1, "Inc": 1, "Max": 255},
#             "CommErrorCountWindow": {"Val": 5, "Min": 0, "Inc": 1, "Max": 20},
#             "ErrorWindow": {"Val": 3600, "Min": 0, "Inc": 5, "Max": 18000},
#             "TimeDeconfirmation": {"Val": 1800, "Min": 0, "Inc": 5, "Max": 10800},
#             "PeriodSensorMin": {"Val": 60, "Min": 20, "Inc": 5, "Max": 2400},
#         }
#     },
#     "Firmware": {
#         "General": {"DowngradeAllow": {"Val": 0, "Min": 0, "Inc": 1, "Max": 1}}
#     },
#     "Azure": {"Connection": {"Enable": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1}}},
# }
