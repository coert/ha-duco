from __future__ import annotations

import importlib.resources as pkg_resources
import logging
import time
from typing import Any

import aiohttp
from aiohttp import TCPConnector

from ...api import certs
from ...api.DTO.ApiDTO import ApiDetailsDTO
from ...api.DTO.InfoDTO import InfoDTO
from ...api.DTO.NodeInfoDTO import NodeDataDTO, NodesDataDTO
from ...api.utils import from_dict, remove_val_fields
from ...const import API_LOCAL_IP, API_PRIVATE_URL
from ..call_handler import get_with_retries
from .apikeygenerator import ApiKeyGenerator
from .cert_handler import CustomSSLContext

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DucoClient:
    @classmethod
    async def create(
        cls,
        api_key: str | None = None,
        private_url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        obj = DucoClient()
        await obj._init(api_key, private_url, session)
        return obj

    async def _init(
        self,
        api_key: str | None = None,
        private_url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        _LOGGER.debug("Initialize Duco API client")

        self._base_url = private_url if private_url else API_PRIVATE_URL
        self._headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        ssl_context = CustomSSLContext(hostname=API_LOCAL_IP)
        ssl_context.load_verify_locations(self._pem())

        self._session = session or aiohttp.ClientSession(
            connector=TCPConnector(ssl=ssl_context)
        )

        if api_key:
            self._headers.update({"Api-Key": api_key})
            self._key = {
                "api_key": api_key,
                "timestamp": time.time(),
            }

        else:
            key_pair = await self.create_api_key()
            api_key = str(key_pair["api_key"])
            self._headers.update({"Api-Key": api_key})
            self._key = key_pair

        _LOGGER.debug(f"Private API endpoint: {self._base_url}")

    def _pem(self):
        pem_path = pkg_resources.files(certs) / "api_cert.pem"
        _LOGGER.debug(f"Loading pem file from {pem_path}")
        return str(pem_path)

    async def close(self):
        try:
            await self._session.close()
        except Exception as e:
            _LOGGER.error(f"Error while closing session: {e}")

    async def create_api_key(self) -> dict[str, str | float]:
        _LOGGER.debug("Creating API key")

        info = await self.get_info()
        duco_mac = info.General.Lan.Mac
        duco_serial = info.General.Board.SerialBoardBox
        duco_time = info.General.Board.Time

        api_key_generator = ApiKeyGenerator()
        key = {
            "api_key": api_key_generator.generate_api_key(
                duco_serial, duco_mac, duco_time
            ),
            "timestamp": time.time(),
        }

        _LOGGER.debug(f"API key created at {time.ctime(key["timestamp"])}")
        return key

    def get_key(self):
        return self._key

    async def get(self, endpoint: str) -> dict[str, Any]:
        data = await get_with_retries(
            f"{self._base_url}{endpoint}", session=self._session, headers=self._headers
        )
        if data:
            return data

        return {}

    async def post(self, endpoint: str):
        async with self._session.post(
            f"{self._base_url}{endpoint}", headers=self._headers
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def patch(self, endpoint: str):
        async with self._session.patch(
            f"{self._base_url}{endpoint}", headers=self._headers
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def delete(self, endpoint: str):
        async with self._session.delete(
            f"{self._base_url}{endpoint}", headers=self._headers
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def head(self, endpoint: str):
        async with self._session.head(
            f"{self._base_url}{endpoint}", headers=self._headers
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def get_api_info(self) -> ApiDetailsDTO:
        _LOGGER.debug("Getting API info")
        api_info_val_dict = await self.get("/api")
        api_info_dict = remove_val_fields(api_info_val_dict)
        return from_dict(ApiDetailsDTO, api_info_dict)  # type: ignore

    async def get_info(self) -> InfoDTO:
        _LOGGER.debug("Getting info")
        info_val_dict = await self.get("/info")
        info_dict = remove_val_fields(info_val_dict)
        return from_dict(InfoDTO, info_dict)  # type: ignore

    async def get_nodes(self) -> NodesDataDTO:
        _LOGGER.debug("Getting info on all nodes")
        nodes_val_dict = await self.get("/info/nodes")
        nodes = [
            from_dict(NodeDataDTO, remove_val_fields(node_dict))
            for node_dict in nodes_val_dict["Nodes"]
        ]
        return from_dict(NodesDataDTO, nodes)  # type: ignore

    async def get_node_info(self, node_id: int) -> NodeDataDTO:
        _LOGGER.debug("Getting node info")
        node_info_val_dict = await self.get(f"/info/nodes/{node_id}")
        node_info_dict = remove_val_fields(node_info_val_dict)
        return from_dict(NodeDataDTO, node_info_dict)  # type: ignore
