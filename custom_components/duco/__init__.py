import inspect

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import DucoDeviceUpdateCoordinator
from .const import LOGGER, DOMAIN, PLATFORMS

type DucoConfigEntry = ConfigEntry[DucoDeviceUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: DucoConfigEntry) -> bool:
    LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")

    coordinator = DucoDeviceUpdateCoordinator(hass)

    try:
        await coordinator.create_api_connection()
        await coordinator.async_config_entry_first_refresh()

    except ConfigEntryNotReady:
        await coordinator.api.rest_handler.close()

        if coordinator.api_disabled:
            entry.async_start_reauth(hass)

        raise

    entry.runtime_data = coordinator

    # Abort reauth config flow if active
    for progress_flow in hass.config_entries.flow.async_progress_by_handler(DOMAIN):
        if (
            "context" in progress_flow
            and progress_flow["context"].get("source") == SOURCE_REAUTH
        ):
            hass.config_entries.flow.async_abort(progress_flow["flow_id"])

    # Finalize
    entry.async_on_unload(coordinator.api.rest_handler.close)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: DucoConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


# async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
#     """Set up Eplucon from a config entry."""
#     _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

#     host: str = config_entry.data["host"]
#     duco_client = await DucoClient.create(hass, private_url=host)

#     box_irbd: str | None = (
#         config_entry.data["box_irbd"] if "box_irbd" in config_entry.data else None
#     )
#     box_index: int | None = (
#         config_entry.data["box_index"] if "box_index" in config_entry.data else None
#     )
#     box_serial_number: str | None = (
#         config_entry.data["box_serial_number"]
#         if "box_serial_number" in config_entry.data
#         else None
#     )
#     box_service_number: str | None = (
#         config_entry.data["box_service_number"]
#         if "box_service_number" in config_entry.data
#         else None
#     )

#     calls = (duco_client.get_info(), duco_client.get_nodes())
#     duco_info, duco_nodes = await asyncio.gather(*calls)
#     duco_node_idxs = {
#         node.Node
#         for node in duco_nodes.Nodes
#         if node.General.Type == "BOX"
#         or node.General.Type == "UCCO2"
#         or node.General.Type == "BSRH"
#     }
#     duco_board = duco_info.General.Board
#     duco_id = duco_board.ProductIdBox
#     assert duco_id, "Invalid data"
#     duco_box_name = duco_board.BoxName
#     assert duco_box_name, "Invalid data"
#     docu_box_sub_type = duco_board.BoxSubTypeName
#     assert docu_box_sub_type, "Invalid data"
#     duco_box_type = " ".join(
#         [word.capitalize() for word in docu_box_sub_type.split("_")]
#     )

#     hass_device_registry = device_registry.async_get(hass)
#     hass_device_registry.async_get_or_create(
#         configuration_url=API_PRIVATE_URL,
#         config_entry_id=config_entry.entry_id,
#         identifiers={(DOMAIN, duco_client.api_key)},
#         manufacturer=MANUFACTURER,
#         suggested_area="Utility Room",
#         name=f"{MANUFACTURER} {duco_box_name.capitalize()} {duco_box_type}",
#         model=duco_box_type,
#     )

#     dto_device = DeviceDTO(
#         id=duco_id,
#         account_module_index=duco_client.api_key,
#         name=duco_box_name,
#         type=duco_box_type,
#         box_irbd=box_irbd,
#         box_index=box_index,
#         box_serial_number=box_serial_number,
#         box_service_number=box_service_number,
#         info=duco_info,
#         nodes=duco_nodes.Nodes,
#     )

#     async def async_update_data() -> DeviceDTO:
#         """Fetch Duco data from API endpoint."""
#         _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore

#         try:
#             calls: list[Coroutine[Any, Any, NodeDataDTO | InfoDTO]] = [
#                 duco_client.get_node_info(idx) for idx in duco_node_idxs
#             ]
#             calls.append(duco_client.get_info())
#             duco_results = await asyncio.gather(*calls)

#             dto_device.nodes.clear()
#             for node_result in duco_results:
#                 if isinstance(node_result, InfoDTO):
#                     dto_device.info = node_result
#                 else:
#                     dto_device.nodes.append(node_result)

#             return dto_device

#         except ApiError as err:
#             _LOGGER.error(f"Error fetching data from Eplucon API: {err}")
#             raise err

#         except Exception as err:
#             _LOGGER.error(
#                 f"Something went wrong when updating Eplucon device from API: {err}"
#             )
#             raise err

#     # Set up the coordinator to manage fetching data from the API
#     coordinator = DataUpdateCoordinator(
#         hass,
#         _LOGGER,
#         name="Duco device",
#         update_method=async_update_data,
#         update_interval=UPDATE_INTERVAL,
#     )

#     # Fetch initial data so we have data when entities subscribe
#     await coordinator.async_config_entry_first_refresh()

#     # Store the coordinator in hass.data, so it's accessible in other parts of the integration
#     hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

#     # Forward the setup to the sensor platform
#     await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

#     return True


# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload a config entry."""
#     unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

#     if unload_ok:
#         hass.data[DOMAIN].pop(entry.entry_id)

#     return unload_ok
