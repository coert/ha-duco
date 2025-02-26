import inspect
import ssl

from ...const import LOGGER


class CustomSSLContext(ssl.SSLContext):
    _hostname: str

    def __new__(cls, hostname: str | None = None, protocol=ssl.PROTOCOL_TLSv1_2):
        LOGGER.debug(f"CustomSSLContext.{inspect.currentframe().f_code.co_name}")

        cls._hostname = hostname or "192.168.4.1"
        return super().__new__(cls, protocol=protocol)

    def wrap_socket(self, *args, **kwargs):
        sock = super().wrap_socket(*args, **kwargs)
        # Perform custom name checking
        hostname = kwargs.get("server_hostname")
        if hostname and not self.custom_name_check(hostname):
            raise ssl.CertificateError(f"Custom name check failed for {hostname}")
        return sock

    def custom_name_check(self, hostname) -> bool:
        # Implement your custom hostname verification logic
        return hostname == self._hostname
