"""
Use jupyter-server-proxy to route requests.
"""

from jupyter_server_proxy.handlers import LocalProxyHandler


class ProxyHandler(LocalProxyHandler):
    def get_current_user(self, *args, **kwargs):
        return "jovyan"

    async def prepare(self, *args, **kwargs):
        # failing upstream
        pass

    def get_port_and_uri(self):
        parts = self.request.uri.split("/")
        port = parts[2]
        uri = "/".join(parts[3:])
        return port, uri

    async def proxy_method(self, method_name, *args, **kwargs):
        port, uri = self.get_port_and_uri()
        method = getattr(super(), method_name)
        await method(port, uri)

    async def http_get(self, *args, **kwargs):
        await self.proxy_method("http_get", *args, **kwargs)

    async def post(self, *args, **kwargs):
        await self.proxy_method("post", *args, **kwargs)

    async def put(self, *args, **kwargs):
        await self.proxy_method("put", *args, **kwargs)

    async def delete(self, *args, **kwargs):
        await self.proxy_method("delete", *args, **kwargs)

    async def head(self, *args, **kwargs):
        await self.proxy_method("head", *args, **kwargs)

    async def patch(self, *args, **kwargs):
        await self.proxy_method("patch", *args, **kwargs)

    async def options(self, *args, **kwargs):
        await self.proxy_method("options", *args, **kwargs)

    async def open(self, *args, **kwargs):
        await self.proxy_method("open", *args, **kwargs)
