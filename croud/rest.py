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
from functools import partial
from typing import List, Optional, Union

from aiohttp import ContentTypeError  # type: ignore
from aiohttp.client_reqrep import ClientResponse

from croud.config import Configuration
from croud.printer import print_error, print_format, print_success
from croud.session import HttpSession, RequestMethod


class Client:
    _env: str
    _token: str
    _region: str
    _output_fmt: str
    _data: Optional[Union[List[dict], dict]] = None
    _error: Optional[dict] = None

    def __init__(
        self, env: str = None, region: str = None, output_fmt: str = None, loop=None
    ):
        self._env = env or Configuration.get_env()
        self._token = Configuration.get_token(self._env)
        self._region = region or Configuration.get_setting("region")
        self._output_fmt = output_fmt or Configuration.get_setting("output_fmt")
        self.loop = loop or asyncio.get_event_loop()

    def send(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        body: dict = None,
        params: dict = None
    ):
        self.loop.run_until_complete(self.fetch(method, endpoint, body, params))

    async def fetch(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ):
        resp = await self._fetch(method, endpoint, body, params)

        self._data, self._error = await self._decode_response(resp)

    async def _fetch(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ) -> ClientResponse:
        async with HttpSession(
            self._env,
            self._token,
            self._region,
            on_new_token=partial(Configuration.set_token, env=self._env),
        ) as session:
            return await session.fetch(method, endpoint, body, params)

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
            data = body["data"] if "data" in body else body
            return data, None

    def print(self, success_message: str = None, keys: List[str] = None):
        if self._error:
            if "message" in self._error:
                print_error(self._error["message"])
            else:
                print_format(self._error, "json")
            return

        if self._data is None:
            message = success_message or "Success."
            print_success(message)
            return

        print_format(self._data, self._output_fmt, keys)
