import asyncio
import logging
from typing import Any

from aiohttp import ClientResponseError, ClientSession, TCPConnector

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def get_with_retries(
    url,
    max_retries=5,
    base_delay=1,
    connector: TCPConnector = None,
    session: ClientSession = None,
    headers: dict[str, str] = None,
) -> dict[str, Any] | None:
    """
    Fetch a URL with retries if a 503 status code is returned.

    Args:
        url (str): The URL to fetch.
        max_retries (int): Maximum number of retries.
        base_delay (float): Base delay in seconds for exponential backoff.
        session (ClientSession): Optional shared aiohttp session.

    Returns:
        Response content or None if all retries fail.
    """
    retries = 0
    while retries < max_retries:
        try:
            # Use a shared session if provided, otherwise create one
            if not session:
                async with ClientSession(connector=connector) as local_session:
                    async with local_session.get(url, headers=headers) as response:
                        if response.status == 503:
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
                async with session.get(url, headers=headers) as response:
                    if response.status == 503:
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
            if e.status == 503:
                retries += 1
                delay = base_delay * (2 ** (retries - 1))  # Exponential backoff
                _LOGGER.warning(
                    f"Retry {retries}/{max_retries}: Waiting {delay:.2f} seconds (503 received)"
                )
                await asyncio.sleep(delay)

            else:
                raise  # Reraise for other HTTP errors

    _LOGGER.warning(f"Failed to fetch {url} after {max_retries} retries.")
    return None
