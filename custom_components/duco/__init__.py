import asyncio
import inspect
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import device_registry

from duco.api.DTO.DeviceDTO import DeviceDTO
from duco.api.DTO.InfoDTO import BoardDTO
from duco.api.private.duco_client import ApiError, DucoClient
from duco.const import API_PRIVATE_URL, DOMAIN, MANUFACTURER, PLATFORMS

_LOGGER = logging.getLogger(__name__)

# Time between data updates
UPDATE_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eplucon from a config entry."""
    _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

    private_url = entry.data.get("api_endpoint", API_PRIVATE_URL)
    session = async_get_clientsession(hass)
    duco_client = await DucoClient.create(session=session, private_url=private_url)

    duco_board: BoardDTO = entry.data["duco_board"]
    box_irbd: str = entry.data["box_irbd"]
    box_index: int = entry.data["box_index"]
    box_serial_number: str = entry.data["box_serial_number"]
    box_service_number: str = entry.data["box_service_number"]

    dto_device = DeviceDTO(
        id=duco_board.ProductIdBox,
        account_module_index=str(duco_client.get_api_key()),
        name=duco_board.BoxName.capitalize(),
        type=" ".join(
            [word.capitalize() for word in duco_board.BoxSubTypeName.split("_")]
        ),
        box_irbd=box_irbd,
        box_index=box_index,
        box_serial_number=box_serial_number,
        box_service_number=box_service_number,
        nodes=[],
        board=duco_board,
    )

    hass_device_registry = device_registry.async_get(hass)
    await register_device(dto_device, entry, hass_device_registry)

    async def async_update_data() -> DeviceDTO:
        """Fetch Duco data from API endpoint."""
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

        try:
            calls = (duco_client.get_info(), duco_client.get_nodes())
            info, nodes = await asyncio.gather(*calls)

            dto_device.lan = info.General.Lan
            dto_device.ventilation = info.Ventilation

            for node in nodes.Nodes:
                dto_device.nodes.append(node)

            return dto_device

        except ApiError as err:
            _LOGGER.error(f"Error fetching data from Eplucon API: {err}")
            raise err

        except Exception as err:
            _LOGGER.error(
                f"Something went wrong when updating Eplucon device from API: {err}"
            )
            raise err

    # Set up the coordinator to manage fetching data from the API
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Duco device",
        update_method=async_update_data,
        update_interval=UPDATE_INTERVAL,
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in hass.data, so it's accessible in other parts of the integration
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def register_device(
    device: DeviceDTO, entry: ConfigEntry, hass_device_registry: DeviceRegistry
):
    _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

    hass_device_registry.async_get_or_create(
        configuration_url=API_PRIVATE_URL,
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, device.account_module_index)},
        manufacturer=MANUFACTURER,
        suggested_area="Utility Room",
        name=device.name,
        model=device.type,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
