"""Diagnostics support for P1 Monitor."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from . import DucoConfigEntry

TO_REDACT = {
    CONF_HOST,
    "serial",
    "wifi_ssid",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: DucoConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = entry.runtime_data.data

    redact_data: dict[str, Any] = {
        "entry": async_redact_data(entry.data, TO_REDACT),
        "data": {
            "info": asdict(data.info) if data.info else None,
            "nodes": [asdict(node) for node in data.nodes],
        },
    }
    return async_redact_data(redact_data, TO_REDACT)
