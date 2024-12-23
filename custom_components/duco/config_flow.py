from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import TextSelector

from .api.private.duco_client import ApiError, DucoClient
from .api.DTO.InfoDTO import InfoDTO
from .const import LOGGER, DOMAIN, MANUFACTURER

# # Define the schema for the user input (API token)
# DATA_SCHEMA = vol.Schema(
#     {
#         vol.Required("api_endpoint", default=API_PRIVATE_URL): selector.TextSelector(
#             selector.TextSelectorConfig(
#                 type=selector.TextSelectorType.URL
#             )  # Using URL text selector
#         ),
#         vol.Optional("box_irbd", default=""): selector.TextSelector(
#             selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#         ),
#         vol.Optional("box_index", default=""): selector.TextSelector(
#             selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#         ),
#         vol.Optional("box_serial_number", default=""): selector.TextSelector(
#             selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#         ),
#         vol.Optional("box_service_number", default=""): selector.TextSelector(
#             selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#         ),
#     }
# )


class DucoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Duco."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        LOGGER.debug("Starting Duco config flow")
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                device_info = await self._async_try_connect(user_input[CONF_HOST])

            except RecoverableError as ex:
                LOGGER.error(ex)
                errors = {"base": ex.error_code}

            else:
                await self.async_set_unique_id(
                    f"{MANUFACTURER}_{device_info.General.Board.BoxName}_{device_info.General.Board.SerialDucoComm}"
                )
                self._abort_if_unique_id_configured(updates=user_input)
                return self.async_create_entry(
                    title=f"{device_info.General.Board.BoxName} {device_info.General.Board.BoxSubTypeName}",
                    data=user_input,
                )
        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=user_input.get(CONF_HOST)
                    ): TextSelector(),
                }
            ),
            errors=errors,
        )

        # if user_input is not None:
        #     api_endpoint = user_input.get("api_endpoint")
        #     box_irbd: str = user_input["box_irbd"] if "box_irbd" in user_input else ""
        #     box_index: str = (
        #         user_input["box_index"] if "box_index" in user_input else ""
        #     )
        #     box_serial_number: str = (
        #         user_input["box_serial_number"]
        #         if "box_serial_number" in user_input
        #         else ""
        #     )
        #     box_service_number: str = (
        #         user_input["box_service_number"]
        #         if "box_service_number" in user_input
        #         else ""
        #     )

        #     # Attempt to connect to the API using the provided API token & endpoint
        #     return self.async_create_entry(
        #         title=MANUFACTURER,
        #         data={
        #             "host": api_endpoint,
        #             "box_irbd": box_irbd,
        #             "box_index": box_index,
        #             "box_serial_number": box_serial_number,
        #             "box_service_number": box_service_number,
        #         },
        #     )

        # else:
        #     # If the user input is not valid or an error occurred, show the form again with the error message
        #     return self.async_show_form(
        #         step_id="user",
        #         data_schema=DATA_SCHEMA,
        #         errors=errors,
        #     )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle discovery via mDNS."""
        LOGGER.debug(f"Discovery info: {discovery_info}")

        valid_names = [f"{DOMAIN}_", f"{DOMAIN} "]

        if not any(discovery_info.name.lower().startswith(x) for x in valid_names):
            return self.async_abort(reason="not_duco_air_device")

        # Extract information from mDNS discovery
        # Use the IP address directly to avoid '.local' issues
        host = f"https://{discovery_info.addresses[0]}"
        unique_id = discovery_info.name.split(" ")[1].strip("[]")

        LOGGER.debug(f"Extracted host: {host}, unique_id: {unique_id}")

        # Check if the device has already been configured
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # Store discovery data in context
        self.context["discovery"] = {  # type: ignore
            "host": host,
            "unique_id": unique_id,
        }

        # Ask user for confirmation
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> ConfigFlowResult:
        """Ask user to confirm adding the discovered device."""
        discovery = self.context["discovery"]  # type: ignore
        host = discovery["host"]
        unique_id = discovery["unique_id"]

        if user_input is not None:
            # Create the entry upon confirmation
            return self.async_create_entry(
                title=MANUFACTURER,
                data={
                    "host": host,
                    "unique_id": unique_id,
                },
            )

        # Show confirmation form to the user
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": host,
                "unique_id": unique_id,
            },
        )

    @staticmethod
    async def _async_try_connect(host: str) -> InfoDTO:
        """Try to connect.

        Make connection with device to test the connection
        and to get info for unique_id.
        """
        try:
            duco_client = DucoClient(host)
            await duco_client.connect_insecure()
            return await duco_client.get_info()

        except ApiError as ex:
            raise RecoverableError(
                "Error occurred while communicating with the Duco device", ""
            ) from ex

        except Exception as ex:
            LOGGER.exception("Unexpected exception")
            raise AbortFlow("unknown_error") from ex


#     @staticmethod
#     @callback
#     def async_get_options_flow(
#         config_entry: config_entries.ConfigEntry,
#     ) -> config_entries.OptionsFlow:
#         """Get the options flow for this handler."""
#         return DucoOptionsFlowHandler(config_entry)


# class DucoOptionsFlowHandler(config_entries.OptionsFlow):
#     """Handle Duco options."""

#     this_config_entry_id: str

#     def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
#         self.this_config_entry_id = config_entry.entry_id

#     async def async_step_init(
#         self, user_input: dict[str, Any] | None = None
#     ) -> ConfigFlowResult:
#         LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
#         """Manage the options for the integration."""
#         errors: dict[str, str] = {}

#         if user_input is not None:
#             config_entry = self.hass.config_entries.async_get_entry(
#                 self.this_config_entry_id
#             )
#             assert config_entry is not None, "Config entry not found"

#             self.hass.config_entries.async_update_entry(
#                 config_entry, options=user_input
#             )
#             host = user_input.get("api_endpoint")
#             box_irbd: str = user_input["box_irbd"] if "box_irbd" in user_input else ""
#             box_index: str = (
#                 user_input["box_index"] if "box_index" in user_input else ""
#             )
#             box_serial_number: str = (
#                 user_input["box_serial_number"]
#                 if "box_serial_number" in user_input
#                 else ""
#             )
#             box_service_number: str = (
#                 user_input["box_service_number"]
#                 if "box_service_number" in user_input
#                 else ""
#             )

#             return self.async_create_entry(
#                 title=MANUFACTURER,
#                 data={
#                     "host": host,
#                     "box_irbd": box_irbd,
#                     "box_index": box_index,
#                     "box_serial_number": box_serial_number,
#                     "box_service_number": box_service_number,
#                 },
#             )

#         # Show the options form with the current API token as the default value
#         return self.async_show_form(
#             step_id="init",
#             data_schema=vol.Schema(
#                 {
#                     vol.Required(
#                         "api_endpoint",
#                         default=self.config_entry.data.get(
#                             "api_endpoint", API_PRIVATE_URL
#                         ),
#                     ): selector.TextSelector(
#                         selector.TextSelectorConfig(
#                             type=selector.TextSelectorType.URL
#                         )  # Using URL text selector
#                     ),
#                     vol.Optional(
#                         "box_irbd",
#                         default=self.config_entry.data.get("box_irbd"),
#                     ): selector.TextSelector(
#                         selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#                     ),
#                     vol.Optional(
#                         "box_index",
#                         default=self.config_entry.data.get("box_index"),
#                     ): selector.TextSelector(
#                         selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#                     ),
#                     vol.Optional(
#                         "box_serial_number",
#                         default=self.config_entry.data.get("box_serial_number"),
#                     ): selector.TextSelector(
#                         selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#                     ),
#                     vol.Optional(
#                         "box_service_number",
#                         default=self.config_entry.data.get("box_service_number"),
#                     ): selector.TextSelector(
#                         selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
#                     ),
#                 }
#             ),
#             errors=errors,
#         )


class RecoverableError(HomeAssistantError):
    """Raised when a connection has been failed but can be retried."""

    def __init__(self, message: str, error_code: str) -> None:
        """Init RecoverableError."""
        super().__init__(message)
        self.error_code = error_code
