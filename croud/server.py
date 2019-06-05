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
from typing import Callable

from aiohttp import web


class Server:
    LOGIN_MSG: str = """
    <b>You have successfully logged into CrateDB Cloud!</b>
    <p>This window can be closed.</p>"""

    PORT: int = 8400

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def create_web_app(self, on_token: Callable[[str], None]) -> web.Application:
        app = web.Application()
        app.add_routes([web.get("/", self.handle_session)])
        app.on_response_prepare.append(self.after_request)  # type: ignore
        self.runner = web.AppRunner(app)
        self.on_token = on_token
        return app

    def handle_session(self, req: web.Request) -> web.Response:
        """Token handler that receives the session token from query param"""
        try:
            self.on_token(req.rel_url.query["token"])
        except KeyError as ex:
            return web.Response(status=500, text=f"No query param {ex!s} in request")
        return web.Response(status=200, text=Server.LOGIN_MSG, content_type="text/html")

    async def after_request(self, req: web.Request, resp: web.Response) -> web.Response:
        """middleware callback right after a request got handled"""
        # stop the event loop right after successful login response
        # so that the Server can be terminated gracefully afterwards
        self.loop.stop()
        return resp

    async def start(self) -> None:
        """Start a local HTTP server"""
        await self.runner.setup()
        site = web.TCPSite(self.runner, "localhost", Server.PORT)
        await site.start()

    async def stop(self) -> None:
        """Shutdown the server gracefully"""
        await self.runner.cleanup()
