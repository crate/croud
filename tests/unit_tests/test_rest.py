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

    def test_send_success_sets_data_with_key(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            data = {"key": "value"}

            client = Client(env="dev", region="bregenz.a1", output_fmt="json")
            client.send(RequestMethod.GET, "/data/data-key")

            assert client._data == data
            assert client._error is None

    def test_send_success_sets_data_without_key(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1", output_fmt="json")
            client.send(RequestMethod.GET, "/data/no-key")

            assert client._data == {"key": "value"}
            assert client._error is None

    def test_send_error_sets_error(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1", output_fmt="json")
            client.send(RequestMethod.GET, "/errors/400")

            assert client._error == {
                "message": "Bad request.",
                "errors": {"key": "Error on 'key'"},
            }

    def test_send_text_response(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1", output_fmt="json")
            client.send(RequestMethod.GET, "/text-response")

            assert client._data is None
            assert client._error == {
                "message": "Invalid response type.",
                "success": False,
            }

    def test_send_empty_response(self, mock_cloud_url, mock_token):
        with mock.patch.object(HttpSession, "_get_conn", return_value=self._get_conn()):
            client = Client(env="dev", region="bregenz.a1", output_fmt="json")
            client.send(RequestMethod.GET, "/empty-response")

            assert client._data is None
            assert client._error is None

    def _get_conn(self):
        return TCPConnector(loop=self.loop, resolver=self.resolver, ssl=True)


@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.rest.print_success")
@mock.patch("croud.rest.print_format")
def test_print_success(mock_print_format, mock_print_success, mock_token, event_loop):
    client = Client(env="dev", region="bregenz.a1", output_fmt="json", loop=event_loop)

    client._data = {"key": "value"}
    client.print()
    mock_print_format.assert_called_once_with({"key": "value"}, "json", None)

    client._data = None
    client.print("Success message.")
    client.print()

    mock_print_success.assert_has_calls(
        [mock.call("Success message."), mock.call("Success.")]
    )


@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.rest.print_error")
def test_print_error(mock_print_error, mock_token, event_loop):
    client = Client(env="dev", region="bregenz.a1", output_fmt="json", loop=event_loop)

    error = {"message": "Bad request.", "errors": {"key": "Error on 'key'"}}
    client._error = error
    client.print()
    mock_print_error.assert_called_once_with("Bad request.")


@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.rest.print_format")
def test_print_error_no_message(mock_print_format, mock_token, event_loop):
    client = Client(env="dev", region="bregenz.a1", output_fmt="json", loop=event_loop)

    error = {"errors": {"key": "Error on 'key'"}}
    client._error = error
    client.print()
    mock_print_format.assert_called_once_with(error, "json")
