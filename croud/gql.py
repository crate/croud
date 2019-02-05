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
from typing import Optional

from croud.config import Configuration
from croud.exceptions import GQLError
from croud.printer import print_error, print_format, print_info
from croud.session import HttpSession
from croud.typing import JsonDict


class Query:
    _query: str
    _env: str
    _output_fmt: str
    _token: str
    _region: str

    def __init__(self, query: str, args: Namespace) -> None:
        self._query = query
        self._token = Configuration.get_token()

        self._set_env(args.env)
        self._set_output_fmt(args)
        self._set_region(args)

        self._error = None
        self._response = None

    def _set_env(self, env: Optional[str]):
        self._env = env or Configuration.get_env()

    def _set_output_fmt(self, args: Namespace):
        if hasattr(args, "output_fmt") and args.output_fmt is not None:
            fmt = args.output_fmt
        else:
            fmt = Configuration.get_setting("output_fmt")

        self._output_fmt = fmt

    def _set_region(self, args: Namespace):
        if hasattr(args, "region") and args.region is not None:
            region = args.region
        else:
            region = Configuration.get_setting("region")

        self._region = region

    async def _fetch_data(self) -> JsonDict:
        async with HttpSession(self._env, self._token, self._region) as session:
            return await session.fetch(self._query)

    def _get_rows(self) -> JsonDict:
        data = self.run()

        if "errors" in data:
            raise GQLError(data["errors"][0]["message"])
        return data["data"]

    def run(self) -> JsonDict:
        loop = asyncio.get_event_loop()

        return loop.run_until_complete(self._fetch_data())

    def execute(self):
        try:
            self._response = self._get_rows()
            self._error = None
        except GQLError as e:
            self._error = str(e)
            self._response = None


def print_query(query: Query, key: str = None):
    if query._error:
        print_error(query._error)
        return

    if not query._response:
        print_info("Result contained no data to print.")
        return

    if not isinstance(query._response, dict):
        print_error("Result has no proper format to print.")
        return

    if key:
        data = query._response[key]
    else:
        data = query._response
    # some queries have two levels to access data
    # e.g. {allProjects: {data: [{projects}]}} vs. {me: {data})
    if "data" in data:
        data = data["data"]

    if len(data) == 0:
        print_info("Result contained no data to print.")
    else:
        print_format(data, query._output_fmt)
