import asyncio
import inspect
import ssl
import orjson
from typing import Any
from urllib.parse import urlparse

from aiohttp import (
    ClientResponseError,
    ClientConnectorDNSError,
    ServerDisconnectedError,
    ClientSession,
    ClientTimeout,
    TCPConnector,
)

from ...const import LOGGER


class RestHandler:
    _max_retries = 5
    _base_delay = 1  # seconds

    _retriable_status_codes = {503}

    _ssl_context: ssl.SSLContext | None
    _connector: TCPConnector | None
    _client_session: ClientSession

    _headers: dict[str, str]

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        ssl_context: ssl.SSLContext | None = None,
        connector: TCPConnector | None = None,
    ):
        self._base_url = base_url
        self._headers = headers
        self._ssl_context = ssl_context
        self._connector = connector
        self._client_session = ClientSession()

        self.headers.update({"Content-Type": "application/json"})

    def __del__(self):
        try:
            asyncio.create_task(self.close())

        except Exception as e:
            LOGGER.warning(f"Error while closing session: {e}")
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

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, value: dict[str, str]):
        self._headers = value

    async def close(self):
        try:
            await self._client_session.close()

        except Exception as e:
            LOGGER.error(f"Error while closing session: {e}")

    async def get(self, endpoint: str) -> dict[str, Any]:
        LOGGER.debug(
            f"{inspect.currentframe().f_code.co_name}  {self._base_url}{endpoint}"
        )

        response_data = await self.get_with_retries(f"{self._base_url}{endpoint}")
        if response_data:
            return response_data

        return {}

    async def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        LOGGER.debug(
            f"{inspect.currentframe().f_code.co_name}  {self._base_url}{endpoint}"
        )

        response_data = await self.post_with_retries(
            f"{self._base_url}{endpoint}", data
        )
        if response_data:
            return response_data

        return {}

    async def patch(self, endpoint: str, data: dict[str, Any]):
        LOGGER.debug(
            f"{inspect.currentframe().f_code.co_name}  {self._base_url}{endpoint}"
        )

        response_data = await self.patch_with_retries(
            f"{self._base_url}{endpoint}", data
        )
        if response_data:
            return response_data

        return {}

    async def delete(self, endpoint: str):
        async with self._client_session.delete(
            f"{self._base_url}{endpoint}",
            headers=self._headers,
            ssl=False,
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def head(self, endpoint: str):
        async with self._client_session.head(
            f"{self._base_url}{endpoint}",
            headers=self._headers,
            ssl=False,
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def patch_with_retries(
        self,
        url: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        data_str = orjson.dumps(data).decode("utf-8")

        retries = 0
        while retries < self.max_retries:
            try:
                async with self._client_session.patch(
                    url,
                    headers=self.headers,
                    ssl=False,
                    timeout=ClientTimeout(total=20000, sock_connect=300),
                    data=data_str,
                ) as response:
                    LOGGER.debug(f"Response status: {response.status}")

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
                    delay = self.base_delay * (2 ** (retries - 1))
                    LOGGER.warning(
                        f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.status} received)"
                    )
                    await asyncio.sleep(delay)

                else:
                    raise  # Reraise for other HTTP errors

            except ClientConnectorDNSError as e:
                LOGGER.error(f"DNS resolution error: {e}")

                urlparsed = urlparse(url)
                if urlparsed.netloc.endswith(".local"):
                    LOGGER.warning(f"Already tried with {url}")
                    raise

                url = urlparsed._replace(netloc=urlparsed.netloc + ".local").geturl()
                LOGGER.warning(f"Retrying with {url}")
                await asyncio.sleep(self.base_delay)

            except ServerDisconnectedError as e:
                LOGGER.error(f"Server disconnected error: {e}")
                retries += 1
                delay = self.base_delay * (2 ** (retries - 1))
                LOGGER.warning(
                    f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.message} received)"
                )
                await asyncio.sleep(delay)

            except Exception as e:
                LOGGER.error(f"{type(e)=}, Error fetching {url}: {e}")
                raise

        LOGGER.warning(f"Failed to post {url} after {self.max_retries} retries.")
        return None

    async def post_with_retries(
        self,
        url: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        data_str = orjson.dumps(data).decode("utf-8")

        retries = 0
        while retries < self.max_retries:
            try:
                async with self._client_session.post(
                    url,
                    headers=self.headers,
                    ssl=False,
                    timeout=ClientTimeout(total=20000, sock_connect=300),
                    data=data_str,
                ) as response:
                    LOGGER.debug(f"Response status: {response.status}")

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
                    delay = self.base_delay * (2 ** (retries - 1))
                    LOGGER.warning(
                        f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.status} received)"
                    )
                    await asyncio.sleep(delay)

                else:
                    raise  # Reraise for other HTTP errors

            except ClientConnectorDNSError as e:
                LOGGER.error(f"DNS resolution error: {e}")

                urlparsed = urlparse(url)
                if urlparsed.netloc.endswith(".local"):
                    LOGGER.warning(f"Already tried with {url}")
                    raise

                url = urlparsed._replace(netloc=urlparsed.netloc + ".local").geturl()
                LOGGER.warning(f"Retrying with {url}")
                await asyncio.sleep(self.base_delay)

            except ServerDisconnectedError as e:
                LOGGER.error(f"Server disconnected error: {e}")
                retries += 1
                delay = self.base_delay * (2 ** (retries - 1))
                LOGGER.warning(
                    f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.message} received)"
                )
                await asyncio.sleep(delay)

            except Exception as e:
                LOGGER.error(f"{type(e)=}, Error fetching {url}: {e}")
                raise

        LOGGER.warning(f"Failed to post {url} after {self.max_retries} retries.")
        return None

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
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

        retries = 0
        while retries < self.max_retries:
            try:
                async with self._client_session.get(
                    url,
                    headers=self._headers,
                    ssl=False,
                    timeout=ClientTimeout(total=20000, sock_connect=300),
                ) as response:  # `ssl=False` skips SSL verification, equivalent to `-k`
                    LOGGER.debug(f"Response status: {response.status}")

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
                    LOGGER.warning(
                        f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.status} received)"
                    )
                    await asyncio.sleep(delay)

                else:
                    raise  # Reraise for other HTTP errors

            except ClientConnectorDNSError as e:
                LOGGER.error(f"DNS resolution error: {e}")

                urlparsed = urlparse(url)
                if urlparsed.netloc.endswith(".local"):
                    LOGGER.warning(f"Already tried with {url}")
                    raise

                url = urlparsed._replace(netloc=urlparsed.netloc + ".local").geturl()
                LOGGER.warning(f"Retrying with {url}")
                await asyncio.sleep(self.base_delay)

            except ServerDisconnectedError as e:
                LOGGER.error(f"Server disconnected error: {e}")
                retries += 1
                delay = self.base_delay * (2 ** (retries - 1))
                LOGGER.warning(
                    f"Retry {retries}/{self.max_retries}: Waiting {delay:.2f} seconds ({e.message} received)"
                )
                await asyncio.sleep(delay)

            except Exception as e:
                LOGGER.error(f"{type(e)=}, Error fetching {url}: {e}")
                raise

        LOGGER.warning(f"Failed to fetch {url} after {self.max_retries} retries.")
        return None
