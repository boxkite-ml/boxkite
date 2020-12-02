import asyncio
import ssl

import aiohttp
import consul.aio

HTTP_SCHEME = "http"
HTTPS_SCHEME = "https"


def get_scheme(use_ssl: bool):
    return HTTPS_SCHEME if use_ssl else HTTP_SCHEME


class PatchedHTTPClient(consul.aio.HTTPClient):
    """Patches py-consul to fix unused self.cert and close error.

    Adapted from: https://github.com/criteo-forks/py-consul/blob/v1.1.1/consul/aio.py

    Changes to `close` taken from unreleased commit f517e49aa986ae44f25ea84db52b17e03d3c123e.
    """

    def __init__(self, *args, loop=None, **kwargs):
        # Skip init of consul.aio.HTTPClient
        super(consul.aio.HTTPClient, self).__init__(*args, **kwargs)
        self._loop = loop or asyncio.get_event_loop()

        sslcontext = (
            ssl.create_default_context(cafile=self.cert) if self.verify else False
        )  # Patched
        connector = aiohttp.TCPConnector(loop=self._loop, ssl=sslcontext)  # Patched
        self._session = aiohttp.ClientSession(connector=connector)

    def close(self):
        return self._session.close()  # Patched


class PatchedConsul(consul.aio.Consul):
    """Patches py-consul to fix unused `cert` param and close error.

    Adapted from: https://github.com/criteo-forks/py-consul/blob/v1.1.1/consul/aio.py

    Changes to `close` taken from unreleased commit f517e49aa986ae44f25ea84db52b17e03d3c123e.
    """

    def connect(self, host, port, scheme, verify=True, cert=None):
        return PatchedHTTPClient(
            host, port, scheme, loop=self._loop, verify=verify, cert=cert
        )  # Patched

    def close(self):
        """Close all opened http connections"""
        return self.http.close()  # Patched
