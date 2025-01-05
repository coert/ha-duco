from __future__ import annotations

import inspect
import logging
import time
import aiohttp
from pathlib import Path
from urllib.parse import urlparse

from dacite import from_dict

from ...api.DTO.ApiDTO import ApiDetailsDTO
from ...api.DTO.InfoDTO import GeneralDTO, InfoDTO
from ...api.DTO.NodeInfoDTO import NodeDataDTO, NodesDataDTO
from ..utils import remove_val_fields
from .rest_handler import RestHandler
from .api_key_generator import ApiKeyGenerator
from .cert_handler import CustomSSLContext

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
        self.host = f"{self.scheme}://{self.netloc}"

        _LOGGER.debug(f"Connecting to {self.host} without SSL verification")

        self._rest_handler = RestHandler(
            self.host, self._headers, aiohttp.TCPConnector(verify_ssl=False)
        )

    async def connect(
        self, ssl_context: CustomSSLContext, api_key: str | None = None
    ) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if api_key:
            self._headers.update({"Api-Key": api_key})
            self._api_key = api_key
            self._api_timestamp = time.time()

        else:
            await self.update_key()

        await self.disconnect()
        self.scheme = "https"
        if self.info_general and self.info_general.Lan.HostName:
            self.netloc = self.info_general.Lan.HostName
        self.host = f"{self.scheme}://{self.netloc}.local"

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self._rest_handler = RestHandler(self.host, self._headers, connector)

    async def disconnect(self) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if self._rest_handler:
            await self._rest_handler.close()
            self._rest_handler = None

    def get_pem_filepath(self):
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        pem_filepath = _FILE_PATH.parents[2] / "certs/api_cert.pem"
        assert pem_filepath.exists(), f"File not found: {pem_filepath}"
        _LOGGER.debug(f"Loading pem file from {pem_filepath.name}")
        return pem_filepath

    async def create_api_key(self, info_general: GeneralDTO) -> dict[str, str | float]:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        duco_mac = info_general.Lan.Mac
        duco_serial = info_general.Board.SerialBoardBox
        duco_time = info_general.Board.Time
        assert duco_mac and duco_serial and duco_time, "Invalid data"

        api_key_generator = ApiKeyGenerator()
        key = {
            "api_key": api_key_generator.generate_api_key(
                duco_serial, duco_mac, duco_time
            ),
            "timestamp": time.time(),
        }

        _LOGGER.debug(f"API key created at {time.ctime(key["timestamp"])}")
        return key

    async def update_key(self) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        if self._info_general:
            self._info_general.Board.Time = int(time.time())  # update time
            key_pair = await self.create_api_key(self._info_general)

        else:
            await self.connect_insecure()
            info = await self.get_info()
            self._info_general = info.General
            key_pair = await self.create_api_key(self._info_general)

        self._headers.update({"Api-Key": str(key_pair["api_key"])})
        self._api_key = str(key_pair["api_key"])
        self._api_timestamp = float(key_pair["timestamp"])

    async def get_api_info(self) -> ApiDetailsDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        api_info_val_dict = await self.rest_handler.get("/api")
        api_info_dict = remove_val_fields(api_info_val_dict)
        return from_dict(ApiDetailsDTO, api_info_dict)  # type: ignore

    async def get_info(self) -> InfoDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        info_val_dict = await self.rest_handler.get("/info")
        info_dict = remove_val_fields(info_val_dict)
        _LOGGER.debug(f"InfoDTO: {info_dict}")
        return from_dict(InfoDTO, info_dict)  # type: ignore

    async def get_nodes(self) -> NodesDataDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        nodes_val_dict = await self.rest_handler.get("/info/nodes")
        nodes = [
            from_dict(NodeDataDTO, remove_val_fields(node_dict))  # type: ignore
            for node_dict in nodes_val_dict["Nodes"]
        ]
        _LOGGER.debug(f"NodesDataDTO: {nodes}")
        return NodesDataDTO(**{"Nodes": nodes})  # type: ignore

    async def get_node_info(self, node_id: int) -> NodeDataDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        node_info_val_dict = await self.rest_handler.get(f"/info/nodes/{node_id}")
        node_info_dict = remove_val_fields(node_info_val_dict)
        _LOGGER.debug(f"NodeDataDTO: {node_info_dict}")
        return from_dict(NodeDataDTO, node_info_dict)  # type: ignore
