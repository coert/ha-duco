"""Update coordinator for Duco."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Coroutine

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.DTO.InfoDTO import InfoDTO
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .api.private.duco_client import ApiError, DucoClient
from .const import DOMAIN, LOGGER, UPDATE_INTERVAL, DeviceResponseEntry


class DucoDeviceUpdateCoordinator(DataUpdateCoordinator[DeviceResponseEntry]):
    api: DucoClient
    api_disabled: bool = False

    _unsupported_error: bool
    _duco_nidxs: set[int]

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str | None = None,
    ) -> None:
        """Initialize update coordinator."""
        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

        self.api_key = api_key
        self.api = DucoClient(self.config_entry.data[CONF_HOST])

        self._unsupported_error = False
        self._duco_nidxs = set()

    async def create_api_connection(self) -> None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        # ssl_context = CustomSSLContext(hostname=self.api.hostname)
        # ssl_context.verify_mode = ssl.CERT_REQUIRED
        # await self.hass.async_add_executor_job(ssl_context.load_default_certs)
        # await self.hass.async_add_executor_job(
        #     ssl_context.load_verify_locations, self.api.get_pem_filepath()
        # )
        await self.api.connect(api_key=self.api_key)
        nodes_data = await self.api.get_nodes()
        self._duco_nidxs = {node.id for node in nodes_data.Nodes}

    async def _async_update_data(self) -> DeviceResponseEntry:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            current_time = asyncio.get_event_loop().time()
            if current_time - self.api.api_timestamp > 60 * 60:  # 1 hour
                await self.api.update_key()

            calls: list[Coroutine[Any, Any, NodeDataDTO | InfoDTO | None]] = [
                self.api.get_node_info(idx) for idx in self._duco_nidxs
            ]
            calls.append(self.api.get_info())
            duco_results = await asyncio.gather(*calls)

            info: InfoDTO | None = None
            nodes: list[NodeDataDTO] = []
            for node_result in duco_results:
                if isinstance(node_result, InfoDTO):
                    info = node_result
                else:
                    nodes.append(node_result)

            assert info is not None, "InfoDTO not found"
            data = DeviceResponseEntry(info=info, nodes=nodes)

        except ApiError as ex:
            LOGGER.error(f"Error fetching data from Duco API: {ex}")

            raise UpdateFailed(
                ex, translation_domain=DOMAIN, translation_key="communication_error"
            ) from ex

        self.api_disabled = False

        self.data = data
        return data
