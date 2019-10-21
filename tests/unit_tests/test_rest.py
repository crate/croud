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

import argparse
import asyncio
from unittest import mock

from aiohttp import TCPConnector  # type: ignore
from aiohttp.test_utils import setup_test_loop, teardown_test_loop
from util.fake_server import FakeCrateDBCloud, FakeResolver

from croud.config import Configuration
from croud.rest import Client
from croud.session import HttpSession, RequestMethod


@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
class TestRestClient:
    @classmethod
    def setup_class(cls):
        cls.loop = setup_test_loop()
        cls.fake_cloud = FakeCrateDBCloud(loop=cls.loop)
        cls.info = cls.loop.run_until_complete(cls.fake_cloud.start())
        cls.resolver = FakeResolver(cls.info, loop=cls.loop)

    @classmethod
    def teardown_class(cls):
        cls.loop.run_until_complete(cls.fake_cloud.stop())
        teardown_test_loop(cls.loop)

    def _get_conn(self):
        return TCPConnector(loop=self.loop, resolver=self.resolver, ssl=True)

    def test_send_success_sets_data_with_key(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            data = {"key": "value"}

            client = Client(env="dev", region="bregenz.a1")
            resp_data, errors = client.send(RequestMethod.GET, "/data/data-key")

            assert resp_data["data"] == data
            assert errors is None

    def test_send_success_sets_data_without_key(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1")
            resp_data, errors = client.send(RequestMethod.GET, "/data/no-key")

            assert resp_data == {"key": "value"}
            assert errors is None

    def test_send_error_sets_error(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1")
            resp_data, errors = client.send(RequestMethod.GET, "/errors/400")
            assert errors == {
                "message": "Bad request.",
                "errors": {"key": "Error on 'key'"},
            }

    def test_send_text_response(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1")
            resp_data, errors = client.send(RequestMethod.GET, "/text-response")

            assert resp_data is None
            assert errors == {"message": "Invalid response type.", "success": False}

    def test_send_empty_response(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1")
            resp_data, errors = client.send(RequestMethod.GET, "/empty-response")

            assert resp_data is None
            assert errors is None

    # If the --sudo argument is given, any value is valid for the header, this
    # checks if the header is set if the --sudo argument was given.
    def test_send_sudo_header_set(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1", sudo=True)
            resp_data, errors = client.send(RequestMethod.GET, f"/test-x-sudo")
            assert resp_data == {}
            assert errors is None

    def test_send_sudo_header_not_set(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1", sudo=False)
            resp_data, errors = client.send(RequestMethod.GET, f"/test-x-sudo")
            assert resp_data == {"message": "Header not set, as expected."}
            assert errors is None

    # This test makes sure that the client is instantiated with the correct arguments,
    # and does not fail if the arguments are in a random positional order.
    def test_client_initialization(self, mock_cloud_url, mock_token):
        args = argparse.Namespace(
            output_fmt="json", sudo=True, region="bregenz.a1", env="dev"
        )
        client = Client.from_args(args)
        assert client._env == "dev"
        assert client._region == "bregenz.a1"
        assert client._sudo is True
        assert isinstance(client.loop, asyncio.AbstractEventLoop)

    def test_error_message_on_connection_error(self, mock_cloud_url, mock_token):
        expected_message = (
            "Failed to perform command on invalid.cratedb.local. "
            "Original error was: 'Cannot connect to host invalid.cratedb.local:443 ssl:None [Name or service not known]' "  # noqa
            "Does the environment exist in the region you specified?"
        )
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            with mock.patch(
                "croud.session.cloud_url", return_value="https://invalid.cratedb.local"
            ):
                client = Client(env="dev", region="bregenz.a1")
                resp_data, errors = client.send(RequestMethod.GET, "/me")
                assert resp_data is None
                assert errors == {"message": expected_message, "success": False}
