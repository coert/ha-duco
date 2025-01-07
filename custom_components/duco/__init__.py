import inspect

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import DucoDeviceUpdateCoordinator

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
