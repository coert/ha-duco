from __future__ import annotations

import inspect
import logging
import time
import orjson
from pathlib import Path
from urllib.parse import urlparse

from dacite import from_dict
from dataclasses import asdict

from ...api.DTO.ApiDTO import ApiDetailsDTO
from ...api.DTO.InfoDTO import GeneralDTO, InfoDTO
from ...api.DTO.NodeInfoDTO import NodeDataDTO, NodesDataDTO
from ...api.DTO.ActionDTO import ActionEnum, NodeActionPostDTO as ActionDTO
from ...api.DTO.NodeActionDTO import NodeActionsDTO
from ..utils import remove_val_fields
from .api_key_generator import ApiKeyGenerator
from .cert_handler import CustomSSLContext
from .rest_handler import RestHandler
from ...const import API_LOCAL_IP

_LOGGER: logging.Logger = logging.getLogger(__package__)

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

    def __init__(self, host: str) -> None:
        self._host = host
        parsed_url = urlparse(host)
        self._scheme = parsed_url.scheme
        self._netloc = parsed_url.netloc

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
    def info_general(self) -> GeneralDTO | None:
        return self._info_general

    @property
    def rest_handler(self) -> RestHandler:
        if self._rest_handler:
            return self._rest_handler

        else:
            raise ApiError("RestHandler not initialized")

    async def connect_insecure(self) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        await self.disconnect()

        self.scheme = "http"
        self.netloc = API_LOCAL_IP
        self.host = f"{self.scheme}://{self.netloc}"

        _LOGGER.debug(f"Connecting to {self.host} without SSL verification")

        self._rest_handler = RestHandler(self.host, self._headers)

    async def connect(self, api_key: str | None = None) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if api_key:
            self._headers.update({"Api-Key": api_key})
            self._api_key = api_key
            self._api_timestamp = time.time() + 3600

        else:
            await self.update_key()

        await self.disconnect()
        self.scheme = "https"
        if self.info_general and self.info_general.Lan.HostName:
            self.netloc = self.info_general.Lan.HostName

        self.host = f"{self.scheme}://{self.netloc}.local"

        self._rest_handler = RestHandler(self.host, self._headers)

    async def disconnect(self) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if self._rest_handler:
            # await self._rest_handler.close()
            self._rest_handler = None

    def get_pem_filepath(self):
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        pem_filepath = _FILE_PATH.parents[2] / "certs/api_cert.pem"
        assert pem_filepath.exists(), f"File not found: {pem_filepath}"
        _LOGGER.debug(f"Loading pem file from {pem_filepath.name}")
        return pem_filepath

    async def _create_api_key(self, info_general: GeneralDTO):
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        duco_mac = info_general.Lan.Mac
        duco_serial = info_general.Board.SerialBoardBox
        duco_time = info_general.Board.Time
        assert duco_mac and duco_serial and duco_time, "Invalid data"

        api_key_generator = ApiKeyGenerator()
        self._api_key = api_key_generator.generate_api_key(
            duco_serial, duco_mac, duco_time
        )

        self._api_timestamp = float(duco_time)
        self._headers.update({"Api-Key": self._api_key})

        if info_general.Board.UpTime:
            up_since = time.time() - info_general.Board.UpTime * 60
            _LOGGER.debug(f"DucoBox up since: {time.ctime(up_since)}")

        _LOGGER.debug(
            f"API key ({self._api_key}) valid until: {time.ctime(self._api_timestamp)}"
        )

    async def update_key(self) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if not self._info_general:
            await self.connect_insecure()
            info = await self.get_info()
            assert info, "Info not found"
            self._info_general = info.General

        await self._create_api_key(self._info_general)

    async def get_api_info(self) -> ApiDetailsDTO | None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            api_info_val_dict = await self.rest_handler.get("/api")
            api_info_dict = remove_val_fields(api_info_val_dict)
            return from_dict(ApiDetailsDTO, api_info_dict)  # type: ignore

        except Exception as e:
            _LOGGER.error(f"Error while getting API info: {e}")
            return None

    async def get_info(self) -> InfoDTO | None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            info_val_dict = await self.rest_handler.get("/info")
            info_dict = remove_val_fields(info_val_dict)
            info = from_dict(InfoDTO, info_dict)  # type: ignore
            self._info_general = info.General
            return info

        except Exception as e:
            _LOGGER.error(f"Error while getting info: {e}")
            return None

    async def get_nodes(self) -> NodesDataDTO | None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            nodes_val_dict = await self.rest_handler.get("/info/nodes")
            nodes = [
                from_dict(NodeDataDTO, remove_val_fields(node_dict))  # type: ignore
                for node_dict in nodes_val_dict["Nodes"]
            ]
            return NodesDataDTO(**{"Nodes": nodes})  # type: ignore

        except Exception as e:
            _LOGGER.error(f"Error while getting nodes: {e}")
            return None

    async def get_node_info(self, node_id: int) -> NodeDataDTO | None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            node_info_val_dict = await self.rest_handler.get(f"/info/nodes/{node_id}")
            node_info_dict = remove_val_fields(node_info_val_dict)
            return from_dict(NodeDataDTO, node_info_dict)  # type: ignore

        except Exception as e:
            _LOGGER.error(f"Error while getting nodes: {e}")
            return None

    async def get_supported_actions(self) -> ActionDTO | None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            supported_actions = await self.rest_handler.get("/action")
            _LOGGER.debug(
                orjson.dumps(supported_actions, option=orjson.OPT_INDENT_2).decode()
            )
            return None

        except Exception as e:
            _LOGGER.error(f"Error while getting supported actions: {e}")
            return None

    async def get_node_supported_actions(self, node_id: int) -> NodeActionsDTO | None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            await self.connect_insecure()
            supported_actions = await self.rest_handler.get(f"/action/nodes/{node_id}")
            return from_dict(NodeActionsDTO, supported_actions)  # type: ignore

        except Exception as e:
            _LOGGER.error(f"Error while getting supported actions: {e}")
            return None

    async def supports_update_ventilation_action(self, node_id: int) -> bool:
        await self.connect_insecure()
        if supported_actions := await self.get_node_supported_actions(node_id):
            for action in supported_actions.Actions:
                if action.Action == "SetVentilationState":
                    return True

        return False

    async def set_ventilation_action(self, node_id: int, action: ActionEnum) -> None:
        try:
            actions = ActionDTO(Action="SetVentilationState", Val=action.value)
            await self.rest_handler.post(f"/action/nodes/{node_id}", asdict(actions))
            _LOGGER.debug(f"Set action {action} for node {node_id}")

        except Exception as e:
            _LOGGER.error(f"Error while setting action: {e}")
