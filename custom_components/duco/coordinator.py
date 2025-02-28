"""Update coordinator for Duco."""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import Any, Coroutine
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.DTO.InfoDTO import InfoDTO
from .api.DTO.NodeInfoDTO import NodeDataDTO
from .api.DTO.NodeActionDTO import NodeActionsDTO
from .api.DTO.NodeConfigDTO import NodeConfigDTO
from .api.private.duco_client import ApiError, DucoClient
from .const import (
    DOMAIN,
    LOGGER,
    API_LOCAL_IP,
    UPDATE_INTERVAL,
    DeviceResponseEntry,
)


class DucoDeviceUpdateCoordinator(DataUpdateCoordinator[DeviceResponseEntry]):
    api: DucoClient
    api_disabled: bool = False

    _unsupported_error: bool
    _duco_nidxs: set[int]

    config_entry: ConfigEntry | None
    data: DeviceResponseEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str | None = None,
    ) -> None:
        """Initialize update coordinator."""
        super().__init__(hass, LOGGER, name=DOMAIN)

        host = (
            self.config_entry.data[CONF_HOST]
            if self.config_entry and CONF_HOST in self.config_entry.data
            else API_LOCAL_IP
        )

        try:
            self.update_interval = (
                timedelta(seconds=float(self.config_entry.data["update_interval"]))
                if self.config_entry and "update_interval" in self.config_entry.data
                else UPDATE_INTERVAL
            )

        except ValueError:
            LOGGER.warning(
                f"Invalid update interval, falling back to default value: {UPDATE_INTERVAL=}"
            )
            self.update_interval = UPDATE_INTERVAL

        self._unsupported_error = False
        self._duco_nidxs = set()

        self.api_key = api_key
        self.api = DucoClient(host)

        self.data = DeviceResponseEntry()

    @property
    def duco_nidxs(self) -> set[int]:
        return self._duco_nidxs

    async def create_api_connection(self) -> None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            await self.api.connect(api_key=self.api_key)

            api_results = await self.api.get_nodes()
            if api_results is not None:
                for node in api_results.Nodes:
                    if node is not None:
                        self.duco_nidxs.add(node.Node)
                        self.data.nodes[node.Node] = node

            calls: list[
                Coroutine[Any, Any, InfoDTO | NodeActionsDTO | NodeConfigDTO | None]
            ] = [self.api.get_node_supported_actions(idx) for idx in self.duco_nidxs]
            calls.extend([self.api.get_node_config(idx) for idx in self.duco_nidxs])
            calls.append(self.api.get_info())
            api_results = await asyncio.gather(*calls)

            for result in api_results:
                if isinstance(result, InfoDTO):
                    self.data.info = result
                elif isinstance(result, NodeActionsDTO):
                    self.data.node_actions[result.Node] = result
                elif isinstance(result, NodeConfigDTO):
                    self.data.node_configs[result.Node] = result

        except ApiError as ex:
            LOGGER.error(f"Error creating connection to Duco API: {ex}")

            raise UpdateFailed(
                ex, translation_domain=DOMAIN, translation_key="communication_error"
            ) from ex

        except Exception as ex:
            LOGGER.error(f"Error creating connection to Duco API: {ex}")

            raise UpdateFailed(
                ex, translation_domain=DOMAIN, translation_key="communication_error"
            ) from ex

    async def _async_update_data(self) -> DeviceResponseEntry:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        try:
            loop_time = asyncio.get_event_loop().time()
            current_time = time.time()
            time_stamp = self.api.api_timestamp
            LOGGER.debug(f"Loop started: {time.ctime(loop_time)} ({loop_time=})")
            LOGGER.debug(f"Current time: {time.ctime(current_time)} ({current_time=})")
            LOGGER.debug(f"Key valid until: {time.ctime(time_stamp)} ({time_stamp=})")

            if current_time > time_stamp:
                await self.api.update_key()

            calls: list[Coroutine[Any, Any, NodeDataDTO | InfoDTO | None]] = [
                self.api.get_node_info(idx) for idx in self.duco_nidxs
            ]
            calls.append(self.api.get_info())
            api_results = await asyncio.gather(*calls)

            if api_results:
                self.data.nodes.clear()
            for result in api_results:
                if isinstance(result, NodeDataDTO):
                    self.data.nodes[result.Node] = result
                elif isinstance(result, InfoDTO):
                    self.data.info = result

        except ApiError as ex:
            LOGGER.error(f"Error fetching data from Duco API: {ex}")

            raise UpdateFailed(
                ex, translation_domain=DOMAIN, translation_key="communication_error"
            ) from ex

        self.api_disabled = False

        return self.data
