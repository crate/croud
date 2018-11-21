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
from typing import Dict

from aiohttp import ClientSession, ContentTypeError, TCPConnector  # type: ignore

from croud.config import Configuration
from croud.printer import print_error
from croud.typing import JsonDict

CLOUD_DEV_HOST: str = "cratedb-dev.cloud"
CLOUD_PROD_HOST: str = "cratedb.cloud"


def run_query(query: str, region: str, env: str) -> JsonDict:
    host = CLOUD_PROD_HOST
    if env.lower() == "dev":
        host = CLOUD_DEV_HOST

    url = f"https://{region}.{host}/graphql"

    conn = TCPConnector()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_query(url, query, conn, headers={}))
    return result


async def _query(url: str, query: str, conn: TCPConnector, headers: Dict[str, str]):
    session = Configuration.read_token()
    async with ClientSession(
        cookies=dict(session=session), connector=conn, headers=headers
    ) as client:
        result = await _fetch(client, url, query)
        return result["data"]


async def _fetch(client: ClientSession, url: str, query: str) -> JsonDict:
    async with client.post(url, json={"query": query}) as resp:
        if resp.status == 200:
            try:
                return await resp.json()
            except ContentTypeError:
                print_error(
                    "Unauthorized. Use `croud login` to login to CrateDB Cloud."
                )
                exit(1)
        else:
            raise Exception(
                f"Query failed to run by returning code of {resp.status}. {query}"
            )
