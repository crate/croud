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
from functools import partial
from typing import Dict, Optional

from croud.config import Configuration
from croud.printer import print_error, print_format, print_info, print_success
from croud.session import HttpSession, RequestMethod
from croud.typing import JsonDict

DEFAULT_ENDPOINT = "/graphql"


class Query:
    def __init__(self, query: str, args: Namespace, endpoint=DEFAULT_ENDPOINT) -> None:
        self._query = query

        self._env = args.env or Configuration.get_env()
        self._token = Configuration.get_token(self._env)
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
        self._endpoint = endpoint

        self._error: Optional[str] = None
        self._response: Optional[JsonDict] = None

    async def _fetch_data(self, body: str, variables: Optional[Dict]) -> JsonDict:
        async with HttpSession(
            self._env,
            self._token,
            self._region,
            on_new_token=partial(Configuration.set_token, env=self._env),
        ) as session:
            resp = await session.fetch(
                RequestMethod.POST,
                self._endpoint,
                {"query": body, "variables": variables},
            )

            if resp.status != 200:
                print_info(f"Query failed to run by returning code of {resp.status}.")
                print_info(body)
                if variables:
                    print_info(str(variables))

            return await resp.json()

    def run(self, body: str, variables: Optional[Dict]) -> JsonDict:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._fetch_data(body, variables))

    def execute(self, variables: Dict = None):
        response = self.run(self._query, variables)

        if "errors" in response:
            self._response = None
            self._error = response["errors"][0]["message"]
        elif "data" in response:
            self._response = response["data"]
            self._error = None
        else:
            self._response = None
            self._error = None


def print_query(query: Query, key: str = None, success_message: str = None) -> None:
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

    if "success" in data:
        success = data["success"]
        if success:
            if success_message:
                print_success(success_message)
            else:
                print_success("Success.")
        else:
            # Edge case that might occur during network partitions/timeouts etc.
            print_error(
                "Command not successful, however no server-side errors occurred. "
                "Please try again."
            )
        return

    # some queries have two levels to access data
    # e.g. {allProjects: {data: [{projects}]}} vs. {me: {data})
    if "data" in data:
        data = data["data"]

    if len(data) == 0:
        print_info("Result contained no data to print.")
    else:
        print_format(data, query._output_fmt)
