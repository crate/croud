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


from unittest import mock

import pytest
from aiohttp.test_utils import TestClient, TestServer

from croud.config import Configuration
from croud.server import Server


@pytest.mark.asyncio
@mock.patch.object(Configuration, "set_token")
async def test_token_handler_and_login(mock_write_token, event_loop):
    server = Server(event_loop)
    app = server.create_web_app(on_token=lambda x: None)
    client = TestClient(TestServer(app), loop=event_loop)
    await client.start_server()

    with mock.patch.object(event_loop, "stop"):  # We exit the server after the request
        resp = await client.get("?token=123")
        assert resp.status == 200
        text = await resp.text()

    assert "You have successfully logged into CrateDB Cloud!" in text

    await client.close()


@pytest.mark.asyncio
@mock.patch.object(Configuration, "set_token")
async def test_token_missing_for_login(mock_write_token, event_loop):
    server = Server(event_loop)
    app = server.create_web_app(on_token=lambda x: None)
    client = TestClient(TestServer(app), loop=event_loop)
    await client.start_server()

    with mock.patch.object(event_loop, "stop"):  # We exit the server after the request
        resp = await client.get("/")
        assert resp.status == 500
        text = await resp.text()

    assert "No query param 'token' in request" in text

    await client.close()
