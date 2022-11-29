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
import os
from argparse import Namespace
from platform import python_version
from typing import Any, Callable, Dict, Optional, Tuple

import requests
from yarl import URL

import croud
from croud.config import CONFIG
from croud.printer import print_debug, print_error, print_info, print_warning

ResponsePair = Tuple[Optional[Dict], Optional[Dict]]


class RequestMethod(enum.Enum):
    DELETE = "delete"
    GET = "get"
    PATCH = "patch"
    POST = "post"
    PUT = "put"


def noop(*args, **kwargs):
    pass


def debug(method, endpoint, params, body):
    if os.getenv("LOG_API", "false").lower() == "true":
        msg = f"{method.upper()} {endpoint}"
        if params:
            msg += f" QS={params}"
        if body:
            msg += f" -> {body}"
        print_debug(msg)


class Client:
    """
    A client for CrateDB Cloud API requests
    """

    def __init__(
        self,
        endpoint: str,
        *,
        token: str = None,
        on_token: Callable = None,
        key: str = None,
        secret: str = None,
        region: str = None,
        sudo: bool = False,
        _verify_ssl: bool = True,
    ):
        """
        :param str endpoint:
          CrateDB Cloud API endpoint
        :param str token:
          The authentication token used as session cookie
        :param Callable on_token:
          A setter method that is called when a new auth token is retrieved
        :param str key:
          The API key used for HTTP basic auth. Note that if both token and key/secret
          are passed, the token takes priority (unless it is None).
        :param str secret:
          The API secret used for HTTP basic auth.
        :param str region:
          Region to get data from or to which to deploy (defines the
          ``X-Region`` HTTP header value)
        :param bool sudo:
          Whether or not to make requests as superuser (defines the
          ``X-Auth-Sudo`` HTTP header value)
        :param bool _verify_ssl:
          A private variable that must only be used during tests!
        """

        self.base_url = URL(endpoint)
        self._token = token
        self._on_token = on_token or noop

        self.session = requests.Session()
        if not token and (key and secret):
            self.session.auth = (key, secret)

        if token and key and secret:
            print_warning(
                "You have both a token and a key/secret set in your profile. "
                "Only the token will be used."
            )

        self.session.cookies["session"] = self._token
        if _verify_ssl is False:
            self.session.verify = False
        if region:
            self.session.headers["X-Region"] = region
        if sudo:
            self.session.headers["X-Auth-Sudo"] = "1"

        ua = f"Croud/{croud.__version__} Python/{python_version()}"
        self.session.headers["User-Agent"] = ua

    @staticmethod
    def from_args(args: Namespace) -> "Client":
        return Client(
            CONFIG.endpoint,
            token=CONFIG.token,
            on_token=CONFIG.set_current_auth_token,
            key=CONFIG.key,
            secret=CONFIG.secret,
            region=args.region or CONFIG.region,
            sudo=args.sudo,
        )

    def request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict = None,
        body: dict = None,
    ):
        # When logging out, the Gateway may respond with a redirect in case the
        # session is still valid and the IDP identifier is present.
        # We need to follow that redirect in order to fully log out the user!
        kwargs: Dict[str, Any] = {
            "allow_redirects": "logout" in endpoint,
        }
        if params is not None:
            kwargs["params"] = params
        if body is not None:
            kwargs["json"] = body

        try:
            url = str(self.base_url.with_path(endpoint))
            debug(method.value, url, params, body)
            response = self.session.request(method.value, url, **kwargs)
        except requests.RequestException as e:
            message = (
                f"Failed to perform request on '{e.request.url}'. "
                f"Original error was: '{e}'"
            )
            return None, {"message": message, "success": False}

        if response.is_redirect:
            redirect_url = URL(response.headers["Location"])
            print_error("Unauthorized.")
            if redirect_url.query.get("rd", "") == endpoint:  # login redirect
                # When use is unauthorized, the API request returns a 302
                # redirect to `/?rd=<api_endpoint>`
                print_info("Use `croud login` to login to CrateDB Cloud.")
            else:
                print_error("Oops. Something unexpected happened.")
            exit(1)

        # Refresh a previously provided token because it has timed out
        response_token = response.cookies.get("session")
        if response_token and response_token != self._token:
            self._token = response_token
            self._on_token(response_token)

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
            body = {"message": f"{resp.status_code} - {resp.reason}", "success": False}

        if resp.status_code >= 400:
            return None, body
        else:
            return body, None
