import asyncio
import aiohttp
import logging
from typing import Any

from aiohttp import ClientResponseError, ClientSession, TCPConnector

_LOGGER: logging.Logger = logging.getLogger(__package__)


class RestHandler:
    _max_retries = 5
    _base_delay = 1  # seconds

    _retriable_status_codes = {503}

    _session: ClientSession

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        connector: TCPConnector,
    ):
        self._base_url = base_url
        self._headers = headers
        self._connector = connector

        self._session = aiohttp.ClientSession(connector=connector)

    def __del__(self):
        if self._session:
            try:
                asyncio.create_task(self.close())

            except Exception as e:
                _LOGGER.warning(f"Error while closing session: {e}")
                asyncio.new_event_loop().run_until_complete(self.close())

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int):
        self._max_retries = value

    @property
    def base_delay(self) -> float:
        return self._base_delay

    @base_delay.setter
    def base_delay(self, value: float):
        self._base_delay = value

    async def close(self):
        try:
            await self._session.close()

        except Exception as e:
            _LOGGER.error(f"Error while closing session: {e}")

    async def get(self, endpoint: str) -> dict[str, Any]:
        data = await self.get_with_retries(f"{self._base_url}{endpoint}")
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

    async def get_with_retries(
        self,
        url: str,
    ) -> dict[str, Any] | None:
        """
        Fetch a URL with retries if a retriable status code is returned.

        Args:
            url (str): The URL to fetch.
            max_retries (int): Maximum number of retries.
            base_delay (float): Base delay in seconds for exponential backoff.
            session (ClientSession): Optional shared aiohttp session.

        Returns:
            Response content or None if all retries fail.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # Use a shared session if provided, otherwise create one
                if not self._session:
                    async with ClientSession(
                        connector=self._connector
                    ) as local_session:
                        async with local_session.get(
                            url, headers=self._headers
                        ) as response:
                            if response.status in self._retriable_status_codes:
                                raise ClientResponseError(
                                    request_info=response.request_info,
                                    history=response.history,
                                    status=response.status,
                                    message="Service Unavailable",
                                )

                            else:
                                response.raise_for_status()

                            return await response.json()
                else:
                    async with self._session.get(
                        url, headers=self._headers
                    ) as response:
                        if response.status in self._retriable_status_codes:
                            raise ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message="Service Unavailable",
                            )

                        else:
                            response.raise_for_status()

                        return await response.json()

            except ClientResponseError as e:
                if e.status in self._retriable_status_codes:
                    retries += 1
                    delay = self.base_delay * (
                        2 ** (retries - 1)
                    )  # Exponential backoff
                    _LOGGER.warning(
                        f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.status} received)"
                    )
                    await asyncio.sleep(delay)

                else:
                    raise  # Reraise for other HTTP errors

        _LOGGER.warning(f"Failed to fetch {url} after {self.max_retries} retries.")
        return None
