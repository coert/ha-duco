import ssl


class CustomSSLContext(ssl.SSLContext):
    def __init__(self, *args, hostname: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._hostname = hostname or "192.168.4.1"
        self.verify_mode = ssl.CERT_REQUIRED
        # Optionally load CA certificates
        self.load_default_certs()

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
