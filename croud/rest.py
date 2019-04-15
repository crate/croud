#!/usr/bin/env python
#
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
from argparse import Namespace
from typing import Dict, Optional, Tuple

from croud.config import Configuration
from croud.printer import print_error, print_format, print_info, print_success
from croud.session import HttpSession, RequestMethod
from croud.typing import JsonDict


class Request:
    def __init__(self, args: Namespace, method: RequestMethod, endpoint: str) -> None:
        self._token = Configuration.get_token()

        self._env = args.env or Configuration.get_env()
        self._output_fmt = (
            hasattr(args, "output_fmt")  # certain commands do not have an output format
            and args.output_fmt
            or Configuration.get_setting("output_fmt")
        )
        self._region = (
            hasattr(args, "region")  # certain commands do not have region
            and args.region
            or Configuration.get_setting("region")
        )
        self._method = method

        self._endpoint = endpoint

        self._error: Optional[str] = None
        self._response: Optional[JsonDict] = None

    async def _fetch_data(self, params: Optional[JsonDict]) -> Tuple[int, JsonDict]:
        async with HttpSession(self._env, self._token, self._region) as session:
            resp = await session.rest_fetch(
                self._method, params, endpoint=self._endpoint
            )
            return resp.status, await resp.json()

    def run(self, params: Optional[JsonDict]) -> Tuple[int, JsonDict]:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._fetch_data(params))

    def send(self, params: Dict = None):
        status, data = self.run(params)

        if status == 302:  # login redirect
            print_error("Unauthorized. Use `croud login` to login to CrateDB Cloud.")
            exit(1)

        if status >= 400:
            self._error = data["error"]["message"]
            return

        self._response = data


def print_response(request: Request, success_message: str = None) -> None:

    if request._error:
        print_error(request._error)
        return

    if not request._response:
        print_info("Result contained no data to print.")
        return

    response = request._response
    if not isinstance(response, dict):
        print_error("Result has no proper format to print.")
        return

    if "data" in response:
        if len(response["data"]) == 0:
            print_info("Result contained no data to print.")
        else:
            print_format(response["data"], request._output_fmt)
    else:
        if success_message:
            print_success(success_message)
        else:
            print_success("Success.")
