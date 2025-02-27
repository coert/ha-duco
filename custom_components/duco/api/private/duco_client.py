from __future__ import annotations

import inspect
import time
from typing import Any
from pathlib import Path
from urllib.parse import urlparse

from dacite import from_dict
from dataclasses import asdict

from ...api.DTO.ApiDTO import ApiDetailsDTO
from ...api.DTO.InfoDTO import GeneralDTO, InfoDTO
from ...api.DTO.NodeInfoDTO import NodeDataDTO, NodesDataDTO
from ...api.DTO.ActionDTO import NodeActionTriggerDTO, NodeActionSetDTO
from ...api.DTO.NodeActionDTO import NodeActionsDTO
from ...const import LOGGER
from ..utils import remove_val_fields
from .api_key_generator import ApiKeyGenerator
from .cert_handler import CustomSSLContext
from .rest_handler import RestHandler

_FILE_PATH = Path(__file__).resolve()


class ApiError(Exception):
    pass


class DucoClient:
    _host: str
    _scheme: str
    _netloc: str
    _headers: dict[str, str]
    _ssl_context: CustomSSLContext

    _rest_handler: RestHandler | None
    _info_general: GeneralDTO | None
    _api_key: str
    _api_timestamp: float
    _api_time_valid: float

    def __init__(self, host: str) -> None:
        self._host = host
        parsed_url = urlparse(host)
        self._scheme = parsed_url.scheme
        self._netloc = parsed_url.netloc
        self._api_time_valid = 3600

        self._headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        self._info_general = None
        self._rest_handler = None

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value

    @property
    def scheme(self) -> str:
        return self._scheme

    @scheme.setter
    def scheme(self, value: str):
        self._scheme = value

    @property
    def hostname(self) -> str:
        return self._netloc

    @property
    def netloc(self) -> str:
        return self._netloc

    @netloc.setter
    def netloc(self, value: str):
        self._netloc = value

    @property
    def ssl_context(self) -> CustomSSLContext:
        return self._ssl_context

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def api_timestamp(self) -> float:
        return self._api_timestamp

    @property
    def api_time_valid(self) -> float:
        return self._api_time_valid

    @property
    def info_general(self) -> GeneralDTO | None:
        return self._info_general

    @property
    def rest_handler(self) -> RestHandler:
        if self._rest_handler:
            return self._rest_handler

        else:
            raise ApiError("RestHandler not initialized")

    async def connect(self, api_key: str | None = None) -> None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if api_key:
            self._headers.update({"Api-Key": api_key})
            self._api_key = api_key
            self._api_timestamp = time.time() + 3600

        else:
            self._rest_handler = RestHandler(self.host, self._headers)
            await self.update_key()
            await self.disconnect()

        LOGGER.debug(f"Connecting to {self.host}")
        self._rest_handler = RestHandler(self.host, self._headers)

    async def disconnect(self) -> None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if self._rest_handler:
            self._rest_handler = None

    def get_pem_filepath(self):
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        pem_filepath = _FILE_PATH.parents[2] / "certs/api_cert.pem"
        assert pem_filepath.exists(), f"File not found: {pem_filepath}"
        LOGGER.debug(f"Loading pem file from {pem_filepath.name}")
        return pem_filepath

    async def _create_api_key(self, info_general: GeneralDTO):
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        duco_mac = info_general.Lan.Mac
        duco_serial = info_general.Board.SerialBoardBox

        if info_general.Board.Time is None:
            duco_time = round(time.time() + self.api_time_valid)

        else:
            duco_time = info_general.Board.Time
            self._api_time_valid = duco_time - time.time()

        assert duco_mac and duco_serial and duco_time, "Invalid data"

        api_key_generator = ApiKeyGenerator()
        self._api_key = api_key_generator.generate_api_key(
            duco_serial, duco_mac, duco_time
        )

        self._api_timestamp = float(duco_time)
        self._headers.update({"Api-Key": self._api_key})

        if info_general.Board.UpTime:
            up_since = time.time() - info_general.Board.UpTime * 60
            LOGGER.debug(f"DucoBox up since: {time.ctime(up_since)}")

        LOGGER.debug(
            f"API key ({self._api_key}) valid until: {time.ctime(self._api_timestamp)} ({self.api_time_valid=})"
        )

    async def update_key(self) -> None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if not self._info_general:
            info = await self.get_info()
            assert info, "Info not found"
            self._info_general = info.General

        else:
            self._info_general.Board.Time = None

        await self._create_api_key(self._info_general)

    async def get_api_info(self) -> ApiDetailsDTO | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            api_info_val_dict = await self.rest_handler.get("/api")
            api_info_dict = remove_val_fields(api_info_val_dict)
            return from_dict(ApiDetailsDTO, api_info_dict)  # type: ignore

        except Exception as e:
            LOGGER.error(f"Error while getting API info: {e}")
            return None

    async def get_info(self) -> InfoDTO | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            info_val_dict = await self.rest_handler.get("/info")
            info_dict = remove_val_fields(info_val_dict)
            info = from_dict(InfoDTO, info_dict)  # type: ignore
            self._info_general = info.General
            return info

        except Exception as e:
            LOGGER.error(f"Error while getting info: {e}")
            return None

    async def get_nodes(self) -> NodesDataDTO | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            nodes_val_dict = await self.rest_handler.get("/info/nodes")
            nodes = [
                from_dict(NodeDataDTO, remove_val_fields(node_dict))  # type: ignore
                for node_dict in nodes_val_dict["Nodes"]
            ]
            return NodesDataDTO(**{"Nodes": nodes})  # type: ignore

        except Exception as e:
            LOGGER.error(f"Error while getting nodes: {e}")
            return None

    async def get_node_info(self, node_id: int) -> NodeDataDTO | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            node_info_val_dict = await self.rest_handler.get(f"/info/nodes/{node_id}")
            node_info_dict = remove_val_fields(node_info_val_dict)
            return from_dict(NodeDataDTO, node_info_dict)  # type: ignore

        except Exception as e:
            LOGGER.error(f"Error while getting nodes: {e}")
            return None

    async def get_node_supported_actions(self, node_id: int) -> NodeActionsDTO | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            supported_actions = await self.rest_handler.get(f"/action/nodes/{node_id}")
            return from_dict(NodeActionsDTO, supported_actions)  # type: ignore

        except Exception as e:
            LOGGER.error(f"Error while getting supported actions: {e}")
            return None

    async def set_node_action_trigger(self, node_id: int, action: str):
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            actions = asdict(NodeActionTriggerDTO(Action=action))
            await self.rest_handler.post(f"/action/nodes/{node_id}", actions)
            LOGGER.debug(f"Triggered action {action} for node {node_id}")

        except Exception as e:
            LOGGER.error(f"Error while getting action state: {e}")

    async def set_node_action_state(self, node_id: int, action: str, state: Any):
        try:
            actions = asdict(NodeActionSetDTO(Action=action, Val=state))
            LOGGER.debug(f"Set action {action} to {state} for node {node_id}")
            LOGGER.debug(f"{actions=}")
            await self.rest_handler.post(f"/action/nodes/{node_id}", actions)

        except Exception as e:
            LOGGER.error(f"Error while setting action: {e}")
