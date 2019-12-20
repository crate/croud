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

import enum
from argparse import Namespace
from typing import Dict, Optional, Tuple

import requests
from yarl import URL

from croud.config import Configuration
from croud.printer import print_error

ResponsePair = Tuple[Optional[Dict], Optional[Dict]]

CLOUD_LOCAL_URL = "http://localhost:8000"
CLOUD_DEV_DOMAIN = "cratedb-dev.cloud"
CLOUD_PROD_DOMAIN = "cratedb.cloud"


class RequestMethod(enum.Enum):
    DELETE = "delete"
    GET = "get"
    PATCH = "patch"
    POST = "post"
    PUT = "put"


class Client:
    def __init__(
        self, *, env: str, region: str, sudo: bool = False, _verify_ssl: bool = True
    ):
        """
        :param bool _verify_ssl: A private variable that must only be used during tests!
        """

        self.env = env or Configuration.get_env()
        self.region = region or Configuration.get_setting("region")
        self.sudo = sudo

        self.base_url = URL(construct_api_base_url(self.env, self.region))

        self._token = Configuration.get_token(self.env)
        self.session = requests.Session()
        if _verify_ssl is False:
            self.session.verify = False
        self.session.cookies["session"] = self._token
        if self.sudo:
            self.session.headers["X-Auth-Sudo"] = "1"

    @staticmethod
    def from_args(args: Namespace) -> "Client":
        return Client(env=args.env, region=args.region, sudo=args.sudo)

    def request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict = None,
        body: dict = None,
    ):
        kwargs: dict = {"allow_redirects": False}
        if params is not None:
            kwargs["params"] = params
        if body is not None:
            kwargs["json"] = body

        try:
            response = self.session.request(
                method.value, str(self.base_url.with_path(endpoint)), **kwargs
            )
        except requests.RequestException as e:
            message = (
                f"Failed to perform command on {e.request.url}. "
                f"Original error was: '{e}' "
                f"Does the environment exist in the region you specified?"
            )
            return None, {"message": message, "success": False}

        if response.is_redirect:  # login redirect
            print_error("Unauthorized. Use `croud login` to login to CrateDB Cloud.")
            exit(1)

        # Refresh a previously provided token because it has timed out
        response_token = response.cookies.get("session")
        if response_token and response_token != self._token:
            self._token = response_token
            Configuration.set_token(response_token, self.env)

        return self.decode_response(response)

    def delete(
        self, endpoint: str, *, params: dict = None, body: dict = None
    ) -> ResponsePair:
        return self.request(RequestMethod.DELETE, endpoint, params=params, body=body)

    def get(self, endpoint: str, *, params: dict = None) -> ResponsePair:
        return self.request(RequestMethod.GET, endpoint, params=params)

    def patch(
        self, endpoint: str, *, params: dict = None, body: dict = None
    ) -> ResponsePair:
        return self.request(RequestMethod.PATCH, endpoint, params=params, body=body)

    def post(
        self, endpoint: str, *, params: dict = None, body: dict = None
    ) -> ResponsePair:
        return self.request(RequestMethod.POST, endpoint, params=params, body=body)

    def put(
        self, endpoint: str, *, params: dict = None, body: dict = None
    ) -> ResponsePair:
        return self.request(RequestMethod.PUT, endpoint, params=params, body=body)

    def decode_response(self, resp: requests.Response) -> ResponsePair:
        if resp.status_code == 204:
            # response is empty
            return None, None

        try:
            # API always returns JSON, unless there's an unhandled server error
            body = resp.json()
        except ValueError:
            body = {"message": "Invalid response type.", "success": False}

        if resp.status_code >= 400:
            return None, body
        else:
            return body, None


def construct_api_base_url(env: str, region: str = "bregenz.a1") -> str:
    if env == "local":
        return CLOUD_LOCAL_URL

    host = CLOUD_DEV_DOMAIN if env == "dev" else CLOUD_PROD_DOMAIN
    return f"https://{region}.{host}"
