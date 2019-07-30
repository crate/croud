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
import uuid
from argparse import Namespace
from functools import partial

from aiohttp import ContentTypeError  # type: ignore
from aiohttp.client_reqrep import ClientResponse

from croud.config import Configuration
from croud.session import HttpSession, RequestMethod


class Client:
    _env: str
    _token: str
    _region: str
    _sudo: bool

    def __init__(self, env: str, region: str, loop=None, sudo: bool = False):
        self._env = env or Configuration.get_env()
        self._token = Configuration.get_token(self._env)
        self._region = region or Configuration.get_setting("region")
        self._sudo = sudo
        self.loop = loop or asyncio.get_event_loop()

    @staticmethod
    def from_args(args: Namespace) -> "Client":
        return Client(env=args.env, region=args.region, sudo=args.sudo)

    def send(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        body: dict = None,
        params: dict = None
    ):
        return self.loop.run_until_complete(self.fetch(method, endpoint, body, params))

    async def fetch(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ):
        async with HttpSession(
            self._env,
            self._token,
            self._region,
            on_new_token=partial(Configuration.set_token, env=self._env),
            headers={"X-Auth-Sudo": str(uuid.uuid4())} if self._sudo is True else {},
        ) as session:
            resp = await session.fetch(method, endpoint, body, params)
            return await self._decode_response(resp)

    async def _decode_response(self, resp: ClientResponse):
        if resp.status == 204:
            # response is empty
            return None, None

        try:
            body = await resp.json()
        # API always returns JSON, unless there's an unhandled server error
        except ContentTypeError:
            body = {"message": "Invalid response type.", "success": False}

        if resp.status >= 400:
            return None, body
        else:
            return body, None
