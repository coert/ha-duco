import inspect
import logging
import ssl

from homeassistant.core import HomeAssistant

_LOGGER: logging.Logger = logging.getLogger(__package__)


class CustomSSLContext(ssl.SSLContext):
    def __init__(self, *args, hostname: str | None = None, **kwargs):
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
        super().__init__(*args, **kwargs)
        self._hostname = hostname or "192.168.4.1"
        self.verify_mode = ssl.CERT_REQUIRED

    async def load_default_certs(
        self, hass: HomeAssistant, purpose: ssl.Purpose = ssl.Purpose.SERVER_AUTH
    ) -> None:
        _LOGGER.debug(f"{inspect.currentframe().f_code.co_name}")  # type: ignore
        # Optionally load CA certificates
        await hass.async_add_executor_job(super().load_default_certs, purpose)

    def wrap_socket(self, *args, **kwargs):
        sock = super().wrap_socket(*args, **kwargs)
        # Perform custom name checking
        hostname = kwargs.get("server_hostname")
        if hostname and not self.custom_name_check(hostname):
            raise ssl.CertificateError(f"Custom name check failed for {hostname}")
        return sock

    def custom_name_check(self, hostname):
        # Implement your custom hostname verification logic
        allowed_hostnames = {self._hostname}
        return hostname in allowed_hostnames
