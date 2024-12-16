import inspect
import logging
from datetime import timedelta
from typing import Any

from dacite import from_dict
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from duco.api.DTO.NodeInfoDTO import NodeDataDTO, NodesDataDTO
from duco.api.private.duco_client import DucoClient
from duco.const import API_PRIVATE_URL, DOMAIN, MANUFACTURER, PLATFORMS

_LOGGER = logging.getLogger(__name__)

# Time between data updates
UPDATE_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eplucon from a config entry."""
    _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
    api_token = entry.data["api_token"]
    api_endpoint = entry.data.get("api_endpoint", API_PRIVATE_URL)

    session = async_get_clientsession(hass)
    duco_client = await DucoClient.create()

    async def async_update_data() -> list[NodeDataDTO]:
        """Fetch Eplucon data from API endpoint."""
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

        return []

    return True
