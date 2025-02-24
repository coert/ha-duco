from dataclasses import dataclass

from .ActionDTO import NodeActionPostDTO as ActionDTO


@dataclass
class ActionsDTO:
    Actions: list[ActionDTO]


@dataclass
class NodeActionsDTO:
    Node: int
    Actions: list[ActionDTO]


@dataclass
class NodesActionsDTO:
    list[NodeActionsDTO]


supported_actions_1 = {
    "Type": "BOX",
    "Node": 1,
    "Actions": [
        {
            "Action": "SetVentilationState",
            "ValType": "Enum",
            "Enum": [
                "AUTO",
                "AUT1",
                "AUT2",
                "AUT3",
                "MAN1",
                "MAN2",
                "MAN3",
                "EMPT",
                "CNT1",
                "CNT2",
                "CNT3",
                "MAN1x2",
                "MAN2x2",
                "MAN3x2",
                "MAN1x3",
                "MAN2x3",
                "MAN3x3",
            ],
        },
        {"Action": "SetParent", "ValType": "Integer"},
        {"Action": "SetAsso", "ValType": "Integer"},
        {"Action": "SetLinkMode", "ValType": "Boolean"},
        {"Action": "SetIdentify", "ValType": "Boolean"},
        {"Action": "Reboot", "ValType": "None"},
        {"Action": "ResetConfig", "ValType": "None"},
    ],
}

supported_actions_2 = {
    "Type": "UCCO2",
    "Node": 2,
    "Actions": [
        {
            "Action": "SetVentilationState",
            "ValType": "Enum",
            "Enum": [
                "AUTO",
                "AUT1",
                "AUT2",
                "AUT3",
                "MAN1",
                "MAN2",
                "MAN3",
                "EMPT",
                "CNT1",
                "CNT2",
                "CNT3",
                "MAN1x2",
                "MAN2x2",
                "MAN3x2",
                "MAN1x3",
                "MAN2x3",
                "MAN3x3",
            ],
        },
        {"Action": "SetParent", "ValType": "Integer"},
        {"Action": "SetAsso", "ValType": "Integer"},
        {"Action": "SetLinkMode", "ValType": "Boolean"},
        {"Action": "SetIdentify", "ValType": "Boolean"},
        {"Action": "Reboot", "ValType": "None"},
        {"Action": "ResetConfig", "ValType": "None"},
    ],
}

supported_actions_3 = {
    "Type": "UCBAT",
    "Node": 3,
    "Actions": [
        {
            "Action": "SetVentilationState",
            "ValType": "Enum",
            "Enum": [
                "AUTO",
                "AUT1",
                "AUT2",
                "AUT3",
                "MAN1",
                "MAN2",
                "MAN3",
                "EMPT",
                "CNT1",
                "CNT2",
                "CNT3",
                "MAN1x2",
                "MAN2x2",
                "MAN3x2",
                "MAN1x3",
                "MAN2x3",
                "MAN3x3",
            ],
        },
        {"Action": "SetParent", "ValType": "Integer"},
        {"Action": "SetAsso", "ValType": "Integer"},
        {"Action": "SetLinkMode", "ValType": "Boolean"},
        {"Action": "SetIdentify", "ValType": "Boolean"},
        {"Action": "Reboot", "ValType": "None"},
        {"Action": "ResetConfig", "ValType": "None"},
    ],
}
