from dataclasses import dataclass
from typing import Optional


@dataclass
class ValRange:
    Val: int
    Min: int
    Inc: int
    Max: int


@dataclass
class NodeConfigDTO:
    Node: int
    SerialBoard: Optional[str]
    SerialDuco: Optional[str]
    FlowLvlAutoMin: Optional[ValRange]
    FlowLvlAutoMax: Optional[ValRange]
    FlowMax: Optional[ValRange]
    FlowLvlMan1: Optional[ValRange]
    FlowLvlMan2: Optional[ValRange]
    FlowLvlMan3: Optional[ValRange]
    TimeMan: Optional[ValRange]
    UcErrorMode: Optional[ValRange]
    Co2SetPoint: Optional[ValRange]
    TempDepEnable: Optional[ValRange]
    ShowSensorLvl: Optional[ValRange]
    Name: Optional[str]


# config_nodes_1 = {
#     "Node": 1,
#     "SerialBoard": "RS2315040973",
#     "SerialDuco": "P284655-231018-008",
#     "FlowLvlAutoMin": {"Val": 30, "Min": 10, "Inc": 5, "Max": 100},
#     "FlowLvlAutoMax": {"Val": 100, "Min": 30, "Inc": 5, "Max": 100},
#     "FlowMax": {"Val": 0, "Min": 0, "Inc": 5, "Max": 750},
#     "FlowLvlMan1": {"Val": 15, "Min": 0, "Inc": 5, "Max": 50},
#     "FlowLvlMan2": {"Val": 50, "Min": 15, "Inc": 5, "Max": 100},
#     "FlowLvlMan3": {"Val": 100, "Min": 50, "Inc": 5, "Max": 100},
#     "TimeMan": {"Val": 15, "Min": 5, "Inc": 5, "Max": 720},
#     "UcErrorMode": {"Val": 1, "Min": 0, "Inc": 1, "Max": 2},
#     "Name": {"Val": ""},
# }

# config_nodes_2 = {
#     "Node": 2,
#     "SerialBoard": "RS2305031916",
#     "SerialDuco": "n/a",
#     "Co2SetPoint": {"Val": 800, "Min": 0, "Inc": 10, "Max": 2000},
#     "FlowLvlMan1": {"Val": 15, "Min": 0, "Inc": 5, "Max": 50},
#     "FlowLvlMan2": {"Val": 50, "Min": 15, "Inc": 5, "Max": 100},
#     "FlowLvlMan3": {"Val": 100, "Min": 50, "Inc": 5, "Max": 100},
#     "TimeMan": {"Val": 15, "Min": 5, "Inc": 5, "Max": 720},
#     "UcErrorMode": {"Val": 1, "Min": 0, "Inc": 1, "Max": 2},
#     "TempDepEnable": {"Val": 1, "Min": 0, "Inc": 1, "Max": 1},
#     "ShowSensorLvl": {"Val": 0, "Min": 0, "Inc": 5, "Max": 100},
#     "Name": {"Val": ""},
# }

# config_nodes_3 = {
#     "Node": 3,
#     "SerialBoard": "n/a",
#     "SerialDuco": "n/a",
#     "FlowLvlMan1": {"Val": 15, "Min": 0, "Inc": 5, "Max": 50},
#     "FlowLvlMan2": {"Val": 50, "Min": 15, "Inc": 5, "Max": 100},
#     "FlowLvlMan3": {"Val": 100, "Min": 50, "Inc": 5, "Max": 100},
#     "TimeMan": {"Val": 15, "Min": 5, "Inc": 5, "Max": 720},
#     "Name": {"Val": ""},
# }
