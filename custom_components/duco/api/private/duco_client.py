from __future__ import annotations

import inspect
import logging
import ssl
import time
from pathlib import Path

import aiohttp
from dacite import from_dict
from homeassistant.core import HomeAssistant

from ...api.DTO.ApiDTO import ApiDetailsDTO
from ...api.DTO.InfoDTO import GeneralDTO, InfoDTO
from ...api.DTO.NodeInfoDTO import NodeDataDTO, NodesDataDTO
from ...const import API_LOCAL_IP, API_PRIVATE_URL
from ..utils import remove_val_fields
from .rest_handler import RestHandler
from .api_key_generator import ApiKeyGenerator
from .cert_handler import CustomSSLContext

_LOGGER: logging.Logger = logging.getLogger(__package__)

_FILE_PATH = Path(__file__).resolve()


class ApiError(Exception):
    pass


class DucoClient:
    _rest_handler: RestHandler
    _api_key: str
    _api_timestamp: float

    @classmethod
    async def create(
        cls,
        hass: HomeAssistant | None = None,
        api_key: str | None = None,
        private_url: str | None = None,
    ):
        obj = DucoClient()
        await obj._init(hass, api_key, private_url)
        return obj

    async def _init(
        self,
        hass: HomeAssistant | None,
        api_key: str | None,
        private_url: str | None,
    ) -> None:
        _LOGGER.debug("Initialize Duco API client")

        self._base_url = private_url if private_url else API_PRIVATE_URL
        self._headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        # Load the certificate using async executor to avoid blocking I/O
        ssl_context = CustomSSLContext(hostname=API_LOCAL_IP)
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        if hass:
            hass.async_add_executor_job(ssl_context.load_default_certs)
            await hass.async_add_executor_job(
                ssl_context.load_verify_locations, self._get_pem_filepath()
            )

        else:
            ssl_context.load_default_certs()
            ssl_context.load_verify_locations(self._get_pem_filepath())

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self._rest_handler = RestHandler(self._base_url, self._headers, connector)

        if api_key:
            key_pair = {
                "api_key": api_key,
                "timestamp": time.time(),
            }
            self._headers.update({"Api-Key": api_key})

        else:
            info = await self.get_info()
            key_pair = await self.create_api_key(info.General)
            self._headers.update({"Api-Key": str(key_pair["api_key"])})

        self._api_key = str(key_pair["api_key"])
        self._api_timestamp = float(key_pair["timestamp"])

        _LOGGER.debug(f"Private API endpoint: {self._base_url}")

    @property
    def rest_handler(self) -> RestHandler:
        return self._rest_handler

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def api_timestamp(self) -> float:
        return self._api_timestamp

    def _get_pem_filepath(self):
        pem_filepath = _FILE_PATH.parents[2] / "certs/api_cert.pem"
        assert pem_filepath.exists(), f"File not found: {pem_filepath}"
        _LOGGER.debug(f"Loading pem file from {pem_filepath.name}")
        return pem_filepath

    async def create_api_key(self, info_general: GeneralDTO) -> dict[str, str | float]:
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

    async def get_api_info(self) -> ApiDetailsDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        api_info_val_dict = await self.rest_handler.get("/api")
        api_info_dict = remove_val_fields(api_info_val_dict)
        return from_dict(ApiDetailsDTO, api_info_dict)  # type: ignore

    async def get_info(self) -> InfoDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        info_val_dict = await self.rest_handler.get("/info")
        info_dict = remove_val_fields(info_val_dict)
        return from_dict(InfoDTO, info_dict)  # type: ignore

    async def get_nodes(self) -> NodesDataDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        nodes_val_dict = await self.rest_handler.get("/info/nodes")
        nodes = [
            from_dict(NodeDataDTO, remove_val_fields(node_dict))  # type: ignore
            for node_dict in nodes_val_dict["Nodes"]
        ]
        return NodesDataDTO(**{"Nodes": nodes})  # type: ignore

    async def get_node_info(self, node_id: int) -> NodeDataDTO:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")
        node_info_val_dict = await self.rest_handler.get(f"/info/nodes/{node_id}")
        node_info_dict = remove_val_fields(node_info_val_dict)
        return from_dict(NodeDataDTO, node_info_dict)  # type: ignore
