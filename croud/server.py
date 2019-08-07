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

from queue import Queue
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib import parse

HOST = "localhost"
PORT = 8400
token_queue = Queue(1)


class SetTokenHTTPServer(ThreadingHTTPServer):
    def __init__(self, on_token: Callable[[str], None], *args, **kwargs):
        self.on_token = on_token
        super().__init__(*args, **kwargs)


class SetTokenHandler(BaseHTTPRequestHandler):
    SUCCESS_MSG = (
        b"<b>You have successfully logged into CrateDB Cloud!</b>"
        b"<p>This window can be closed.</p>"
    )
    MISSING_TOKEN_MSG = (
        b"<b>Login to CrateDB Cloud failed!</b>"
        b"<p>Authentication token missing in URL.</p>"
    )
    DUPLICATE_TOKEN_MSG = (
        b"<b>Login to CrateDB Cloud failed!</b>"
        b"<p>More than one authentication token present in URL.</p>"
    )

    def do_GET(self):
        query_string = parse.urlparse(self.path).query
        query = parse.parse_qs(query_string)
        if "token" not in query:
            code = 400
            msg = SetTokenHandler.MISSING_TOKEN_MSG
        elif len(query["token"]) != 1:
            code = 400
            msg = SetTokenHandler.DUPLICATE_TOKEN_MSG
        else:
            token = query["token"][0]
            token_queue.put(token)
            code = 200
            msg = SetTokenHandler.SUCCESS_MSG
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)
        self.server.shutdown()

    def log_request(self, code='-', size='-'):
        pass


def run_server(on_token) -> Thread:
    server = SetTokenHTTPServer(on_token, (HOST, PORT), SetTokenHandler)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server_thread
