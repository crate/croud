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

import ssl
from enum import Enum
from types import TracebackType
from typing import Callable, Dict, Optional, Type

import certifi
from aiohttp import ClientResponse, ClientSession, TCPConnector  # type: ignore

from croud.printer import print_error

CLOUD_LOCAL_URL = "http://localhost:8000"
CLOUD_DEV_DOMAIN = "cratedb-dev.cloud"
CLOUD_PROD_DOMAIN = "cratedb.cloud"


class RequestMethod(Enum):
    GET = "get"
    POST = "post"
    DELETE = "delete"
    PATCH = "patch"
    PUT = "put"


class HttpSession:
    def __init__(
        self,
        env: str,
        token: str,
        region: str = "bregenz.a1",
        url: Optional[str] = None,
        conn: Optional[TCPConnector] = None,
        headers: Dict[str, str] = {},
        on_new_token: Callable[[str], None] = None,
    ) -> None:
        self.env = env
        self.token = token
        self.on_new_token = on_new_token

        if not url:
            url = cloud_url(env, region)

        self.url = url
        if conn is None:
            conn = self._get_conn()

        self.client = ClientSession(
            cookies={"session": self.token}, connector=conn, headers=headers
        )

    def _get_conn(self) -> TCPConnector:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        return TCPConnector(ssl_context=ssl_context)

    async def fetch(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ) -> ClientResponse:
        url = self.url + endpoint
        resp = await getattr(self.client, method.value)(
            url, json=body, allow_redirects=False, params=params
        )
        if resp.status == 302:  # login redirect
            print_error("Unauthorized. Use `croud login` to login to CrateDB Cloud.")
            exit(1)
        return resp

    async def logout(self, url: str):
        await self.client.get(url)

    async def __aenter__(self) -> "HttpSession":
        return self

    async def close(self) -> None:
        new_token = self.client.cookie_jar.filter_cookies(self.url).get("session")
        if new_token and self.token != new_token.value and self.on_new_token:
            self.on_new_token(new_token.value)
        await self.client.close()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()


def cloud_url(env: str, region: str = "bregenz.a1") -> str:
    if env == "local":
        return CLOUD_LOCAL_URL

    host = CLOUD_DEV_DOMAIN if env == "dev" else CLOUD_PROD_DOMAIN
    return f"https://{region}.{host}"
