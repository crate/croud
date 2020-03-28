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

import json
import pathlib
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Callable, Dict
from urllib import parse


class Response:
    __slots__ = ("bytes", "status", "headers")

    def __init__(self, *, text=None, json_data=None, status=200, headers=None):
        self.status = status
        self.headers = headers or {}
        if json_data is not None:
            self.headers.setdefault("Content-Type", "application/json")
            text = json.dumps(json_data)
        else:
            text = text or ""
            self.headers.setdefault("Content-Type", "text/html")

        self.bytes = text.encode()
        self.headers["Content-Length"] = len(self.bytes)


class FakeCrateDBCloudServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load certificates and sign key used to simulate ssl/tls
        here = pathlib.Path(__file__)
        self.ssl_cert = here.parent / "server.crt"
        ssl_key = here.parent / "server.key"
        self.socket = ssl.wrap_socket(
            self.socket,
            keyfile=str(ssl_key),
            certfile=str(self.ssl_cert),
            server_side=True,
        )


class FakeCrateDBCloudRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes: Dict[str, Callable[[], Response]] = {
            "/data/data-key": self.data_data_key,
            "/data/no-key": self.data_no_key,
            "/errors/400": self.error_400,
            "/text-response": self.text_response,
            "/empty-response": self.empty_response,
            "/redirect": self.redirect,
            "/new-token": self.new_token,
            "/client-headers": self.client_headers,
        }
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed = parse.urlparse(self.path)
        self.request_path = parsed.path
        self.query = parse.parse_qs(parsed.query)

        body_length = int(self.headers.get("Content-Length", 0))
        if body_length > 0:
            self.body = self.rfile.read(body_length)
        else:
            self.body = None

        self.cookies = dict(
            cookie.split("=", 1)
            for cookie in self.headers.get_all("cookie", [])
            if cookie
        )

        handler = self.routes.get(self.request_path, self.default_response)

        response = handler()
        self.send_response(response.status)
        for header, value in response.headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response.bytes)

    do_DELETE = do_GET
    do_HEAD = do_GET
    do_PATCH = do_GET
    do_POST = do_GET
    do_PUT = do_GET

    def default_response(self) -> Response:
        return Response(
            json_data={
                "body": self.body,
                "headers": dict(self.headers),  # type: ignore
                "method": self.command,
                "path": self.request_path,
                "query": self.query,
            },
            status=404,
        )

    def data_data_key(self) -> Response:
        if self.is_authorized:
            return Response(json_data={"data": {"key": "value"}}, status=200)
        return Response(status=302, headers={"Location": "/"})

    def data_no_key(self) -> Response:
        if self.is_authorized:
            return Response(json_data={"key": "value"})
        return Response(status=302, headers={"Location": "/"})

    def error_400(self) -> Response:
        if self.is_authorized:
            return Response(
                json_data={
                    "message": "Bad request.",
                    "errors": {"key": "Error on 'key'"},
                },
                status=400,
            )

        return Response(status=302, headers={"Location": "/"})

    def text_response(self) -> Response:
        if self.is_authorized:
            return Response(text="Non JSON response.", status=500)
        return Response(status=302, headers={"Location": "/"})

    def empty_response(self) -> Response:
        if self.is_authorized:
            return Response(status=204)
        return Response(status=302, headers={"Location": "/"})

    def redirect(self) -> Response:
        return Response(status=301, headers={"Location": "/?rd=%2Fredirect"})

    def new_token(self) -> Response:
        return Response(
            status=204, headers={"Set-Cookie": "session=new-token; Domain=127.0.0.1"}
        )

    def client_headers(self) -> Response:
        return Response(json_data=dict(self.headers.items()))

    @property
    def is_authorized(self) -> bool:
        if "session" in self.cookies:
            if self.cookies["session"]:
                return True
        return False

    def log_message(self, *args, **kwargs):
        # Don't log anything during tests.
        pass


class FakeCrateDBCloud:
    def __init__(self):
        self._server = FakeCrateDBCloudServer(
            ("127.0.0.1", 0), FakeCrateDBCloudRequestHandler
        )
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    def start_in_background(self) -> "FakeCrateDBCloud":
        self._thread.start()
        return self

    def wait_for_shutdown(self):
        self._server.shutdown()

    @property
    def port(self):
        return self._server.socket.getsockname()[1]

    def __enter__(self):
        return self.start_in_background()

    def __exit__(self, exc_type, exc_value, traceback):
        self.wait_for_shutdown()
