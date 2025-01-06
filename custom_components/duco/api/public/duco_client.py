from __future__ import annotations

import logging

import aiohttp
import orjson

from ...const import API_PUBLIC_URL

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DucoClient:
    @classmethod
    async def create(
        cls,
        primary_key: str,
        secondary_key: str | None = None,
        public_url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        obj = DucoClient()
        await obj._init(primary_key, secondary_key, public_url, session)
        return obj

    async def _init(
        self,
        primary_key: str,
        secondary_key: str | None = None,
        public_url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._primary_key = primary_key
        self._secondary_key = secondary_key
        self._base_url = public_url if public_url else API_PUBLIC_URL
        self._session = session or aiohttp.ClientSession()

        self._headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Api-Subscription-Key": primary_key,
        }

        _LOGGER.debug("Initialize Duco API client")
        _LOGGER.debug(f"Public API endpoint: {self._base_url}")
        _LOGGER.debug(f"Headers: {self._headers}")

    async def close(self):
        await self._session.close()

    async def get_info(self):
        _LOGGER.debug("Getting info")

        async with self._session.get(
            f"{self._base_url}/health", headers=self._headers
        ) as response:
            _LOGGER.debug(f"{response.status=}")
            data = await response.json()
            _LOGGER.debug(data)
            response.raise_for_status()
            return

    async def register_device(self, serial_number: str):
        _LOGGER.debug(f"Registering device with serial number: {serial_number}")
        _LOGGER.debug(orjson.dumps(self._headers, option=orjson.OPT_INDENT_2).decode())

        async with self._session.post(
            f"{self._base_url}/devices",
            json={"SerialNumber": serial_number},
            headers=self._headers,
        ) as response:
            _LOGGER.debug(f"{response.status=}")
            data = await response.json()
            _LOGGER.debug(data)
            response.raise_for_status()
            return data
