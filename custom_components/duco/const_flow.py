import logging

import voluptuous as vol

from .const import API_PRIVATE_URL

_LOGGER = logging.getLogger(__name__)


# Define the schema for the user input (API token)
DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_token"): str,
        vol.Required("api_endpoint", default=API_PRIVATE_URL): str,
    }
)
