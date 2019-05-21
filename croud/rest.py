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

    def __init__(self, env: str = None, region: str = None, output_fmt: str = None):
        self._env = env or Configuration.get_env()
        self._region = region or Configuration.get_setting("region")
        self._output_fmt = output_fmt or Configuration.get_setting("output_fmt")

    def send(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        body: dict = None,
        params: dict = None
    ):
        resp = self._run(method, endpoint, body, params)
        data = self._decode_response(resp)

        if resp.status >= 400:
            self._error = data
            return

        self._data = data["data"] if "data" in data else data

    def print(self, success_message: str = None, keys: List[str] = None):
        if self._error:
            if "message" in self._error:
                print_error(self._error["message"])
            else:
                print_format(self._error, "json")
            return

        if self._data is None or len(self._data) == 0:
            message = success_message or "Success."
            print_success(message)
            return

        print_format(self._data, self._output_fmt, keys)

    def _run(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ) -> ClientResponse:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._fetch_data(method, endpoint, body, params))

    async def _fetch_data(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ) -> ClientResponse:
        async with HttpSession(
            self._env, Configuration.get_token(), self._region
        ) as session:
            return await session.fetch(method, endpoint, body, params)

    def _decode_response(self, resp: ClientResponse):
        async def _decode():
            try:
                return await resp.json()
            # API always returns JSON, unless there's an unhandled server error
            except ContentTypeError:
                return {"message": "Invalid response type.", "success": False}

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_decode())
