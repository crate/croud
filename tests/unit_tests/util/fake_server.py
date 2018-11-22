# Licensed to CRATE Technology GmbH ("Crate") under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  Crate licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
# However, if you have executed another commercial license agreement
# with Crate these terms will supersede the license and you may use the
# software solely pursuant to the terms of the relevant commercial agreement.

import asyncio
import pathlib
import socket
import ssl
from typing import Any, Dict, Iterable

from aiohttp import web
from aiohttp.resolver import DefaultResolver
from aiohttp.test_utils import unused_port


class FakeResolver:
    _LOCAL_HOST = {0: "127.0.0.1", socket.AF_INET: "127.0.0.1", socket.AF_INET6: "::1"}

    def __init__(self, fakes, loop: asyncio.AbstractEventLoop):
        """fakes -- dns -> port dict"""
        self._fakes = fakes
        self._resolver = DefaultResolver(loop=loop)

    async def resolve(
        self, host: str, port: int = 0, family: socket.AddressFamily = socket.AF_INET
    ) -> Iterable[Dict[str, Any]]:
        fake_port = self._fakes.get(host)
        if fake_port is not None:
            return [
                {
                    "hostname": host,
                    "host": self._LOCAL_HOST[family],
                    "port": fake_port,
                    "family": family,
                    "proto": 0,
                    "flags": socket.AI_NUMERICHOST,
                }
            ]
        else:
            return await self._resolver.resolve(host, port, family)


class FakeCrateDBCloud:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.app = web.Application()
        # thi will allow us to register multiple endpoints/handlers to test
        self.app.router.add_routes([web.post("/graphql", self.on_graphql)])
        here = pathlib.Path(__file__)
        # Load certificates and sign key used to simulate ssl/tls
        ssl_cert = here.parent / "server.crt"
        ssl_key = here.parent / "server.key"
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(str(ssl_cert), str(ssl_key))

    async def start(self) -> Dict[str, int]:
        port = unused_port()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "localhost", port, ssl_context=self.ssl_context)
        await site.start()
        return {"cratedb.local": port}

    async def stop(self) -> None:
        await self.runner.cleanup()

    async def on_graphql(self, request: web.Request) -> web.Response:
        if self._is_authorized(request):
            if self._get_query_header(request) == "me":
                return web.json_response(
                    {
                        "data": {
                            "me": {
                                "email": "sheldon@crate.io",
                                "username": "Google_1234",
                                "name": "Sheldon Cooper",
                            }
                        }
                    }
                )
        # If the session cookie is invalid the OAuth Proxy will serve the
        # provider sign-in page (status = 200) instead of a 401 Unauthorized
        return web.Response(status=200, text="OAuth provider sign-in page")

    def _is_authorized(self, request: web.Request) -> bool:
        if "session" in request.cookies:
            if request.cookies["session"]:
                return True
        return False

    def _get_query_header(self, request: web.Request) -> str:
        if request.content_type == "application/json":
            if "query" in request.headers:
                if request.headers["query"] == "me":
                    return "me"
                else:
                    return ""
        return ""
