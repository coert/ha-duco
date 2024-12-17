import inspect
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback

from .api.private.duco_client import ApiError, DucoClient
from .const import API_PRIVATE_URL, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


# Define the schema for the user input (API token)
DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_endpoint", default=API_PRIVATE_URL): str,
        vol.Optional("box_irbd"): str,
        vol.Optional("box_index"): str,
        vol.Optional("box_serial_number"): str,
        vol.Optional("box_service_number"): str,
    }
)


class DucoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Duco."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        _LOGGER.debug("Starting Duco config flow")

        if user_input is not None:
            # Attempt to connect to the API using the provided API token & endpoint
            api_endpoint: str = user_input["api_endpoint"]
            box_irbd: str = user_input["box_irbd"] if "box_irbd" in user_input else ""
            box_index: str = (
                user_input["box_index"] if "box_index" in user_input else ""
            )
            box_serial_number: str = (
                user_input["box_serial_number"]
                if "box_serial_number" in user_input
                else ""
            )
            box_service_number: str = (
                user_input["box_service_number"]
                if "box_service_number" in user_input
                else ""
            )

            client = await DucoClient.create(private_url=api_endpoint)

            try:
                info = await client.get_info()

                duco_board = info.General.Board
                duco_lan = info.General.Lan

                return self.async_create_entry(
                    title=MANUFACTURER,
                    data={
                        "duco_board": duco_board,
                        "duco_lan": duco_lan,
                        "box_irbd": box_irbd,
                        "box_index": box_index,
                        "box_serial_number": box_serial_number,
                        "box_service_number": box_service_number,
                    },
                )

            except ApiError:
                # Handle general API error
                _LOGGER.info("Failed to fetch devices from Duco API")
                errors["base"] = "api"

            except Exception as e:
                # Handle any other unexpected exceptions
                _LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"

            finally:
                await client.close()

        # If the user input is not valid or an error occurred, show the form again with the error message
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return DucoOptionsFlowHandler(config_entry)


class DucoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Duco options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize Duco options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
        """Manage the options for the integration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_endpoint = user_input.get("api_endpoint")
            box_irbd: str = user_input["box_irbd"] if "box_irbd" in user_input else ""
            box_index: str = (
                user_input["box_index"] if "box_index" in user_input else ""
            )
            box_serial_number: str = (
                user_input["box_serial_number"]
                if "box_serial_number" in user_input
                else ""
            )
            box_service_number: str = (
                user_input["box_service_number"]
                if "box_service_number" in user_input
                else ""
            )
            client = await DucoClient.create(private_url=api_endpoint)

            try:
                info = await client.get_info()

                duco_board = info.General.Board
                duco_lan = info.General.Lan

                return self.async_create_entry(
                    title=MANUFACTURER,
                    data={
                        "duco_board": duco_board,
                        "duco_lan": duco_lan,
                        "box_irbd": box_irbd,
                        "box_index": box_index,
                        "box_serial_number": box_serial_number,
                        "box_service_number": box_service_number,
                    },
                )

            except ApiError:
                # Handle general API error
                _LOGGER.info("Failed to fetch devices from Duco API")
                errors["base"] = "api"

            except Exception as e:
                # Handle any other unexpected exceptions
                _LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"

            finally:
                await client.close()

        # Show the options form with the current API token as the default value
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "api_endpoint",
                        default=self.config_entry.data.get(
                            "api_endpoint", API_PRIVATE_URL
                        ),
                    ): str,
                    vol.Required(
                        "box_irbd",
                        default=self.config_entry.data.get("box_irbd"),
                    ): str,
                    vol.Required(
                        "box_index",
                        default=self.config_entry.data.get("box_index"),
                    ): str,
                    vol.Required(
                        "box_serial_number",
                        default=self.config_entry.data.get("box_serial_number"),
                    ): str,
                    vol.Required(
                        "box_service_number",
                        default=self.config_entry.data.get("box_service_number"),
                    ): str,
                }
            ),
            errors=errors,
        )
