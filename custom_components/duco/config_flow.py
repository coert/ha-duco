from typing import Any, Optional
import inspect
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import TextSelector

from .api.DTO.InfoDTO import InfoDTO
from .api.private.duco_client import ApiError, DucoClient
from .const import DOMAIN, LOGGER, MANUFACTURER, API_PRIVATE_URL, UPDATE_INTERVAL

# Define the schema for the user input (API token)
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=API_PRIVATE_URL): TextSelector(),
        vol.Required(
            "update_interval", default=int(UPDATE_INTERVAL.total_seconds())
        ): int,
    }
)


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
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return DucoOptionsFlowHandler()

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
        discovery = {
            "host": host,
            "update_interval": int(UPDATE_INTERVAL.total_seconds()),
            "unique_id": unique_id,
        }
        self.context["discovery"] = discovery  # type: ignore

        # Ask user for confirmation
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask user to confirm adding the discovered device."""
        discovery = self.context["discovery"]  # type: ignore
        host = discovery["host"]
        update_interval = discovery["update_interval"]
        unique_id = discovery["unique_id"]

        if user_input is not None:
            # Create the entry upon confirmation
            return self.async_create_entry(
                title=MANUFACTURER,
                data={
                    "host": user_input["host"],
                    "update_interval": user_input["update_interval"],
                    "unique_id": unique_id,
                },
            )

        # Show confirmation form to the user
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": host,
                "update_interval": update_interval,
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
            info = await duco_client.get_info()
            assert info is not None, "InfoDTO not found"
            return info

        except ApiError as ex:
            raise RecoverableError(
                "Error occurred while communicating with the Duco device", ""
            ) from ex

        except Exception as ex:
            LOGGER.exception("Unexpected exception")
            raise AbortFlow("unknown_error") from ex


class DucoOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self) -> None:
        """Initialize Duco options flow."""
        # self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> ConfigFlowResult:
        LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
        """Manage the options for the integration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # If the user has provided new data, update the config entry
            host = str(user_input.get("host"))
            update_interval = user_input.get("update_interval")

            try:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={"host": host, "update_interval": update_interval},
                )
                return self.async_create_entry(title="", data={})

            except ApiError:
                # Handle general API error
                LOGGER.info("Failed to fetch devices from Eplucon API")
                errors["base"] = "api"

            except Exception as e:
                # Handle any other unexpected exceptions
                LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"

        # Show the options form with the current API token as the default value
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "host",
                        default=self.config_entry.data.get("host", API_PRIVATE_URL),
                    ): str,
                    vol.Required(
                        "update_interval",
                        default=self.config_entry.data.get(
                            "update_interval", int(UPDATE_INTERVAL.total_seconds())
                        ),
                    ): str,
                }
            ),
            errors=errors,
        )


class RecoverableError(HomeAssistantError):
    """Raised when a connection has been failed but can be retried."""

    def __init__(self, message: str, error_code: str) -> None:
        """Init RecoverableError."""
        super().__init__(message)
        self.error_code = error_code
