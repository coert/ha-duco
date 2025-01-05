from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .api.DTO.DeviceDTO import DeviceDTO
from .const import LOGGER, DOMAIN, MANUFACTURER


class DucoDevice:
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        device: DeviceDTO,
    ) -> None:
        LOGGER.info(f"Init DucoDevice with id '{device.id}'")
        self.device_registry = dr.async_get(hass)
        self.device = self.device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            name=f"Duco {device.name}",
            model=f"{device.type}",
            manufacturer=MANUFACTURER,
            identifiers={(DOMAIN, f"Duco {device.id}")},
        )
