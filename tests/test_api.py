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
import re
from unittest import mock

import pytest

from croud.api import Client, construct_api_base_url


def test_send_success_sets_data_with_key(client: Client):
    resp_data, errors = client.get("/data/data-key")
    assert resp_data == {"data": {"key": "value"}}
    assert errors is None


def test_send_success_sets_data_without_key(client: Client):
    resp_data, errors = client.get("/data/no-key")
    assert resp_data == {"key": "value"}
    assert errors is None


def test_send_error_sets_error(client: Client):
    resp_data, errors = client.get("/errors/400")
    assert errors == {"message": "Bad request.", "errors": {"key": "Error on 'key'"}}


def test_send_text_response(client: Client):
    resp_data, errors = client.get("/text-response")
    assert resp_data is None
    assert errors == {"message": "Invalid response type.", "success": False}


def test_send_empty_response(client: Client):
    resp_data, errors = client.get("/empty-response")
    assert resp_data is None
    assert errors is None


def test_send_redirect_response(client: Client, capsys):
    with pytest.raises(SystemExit):
        client.get("/redirect")
    _, err = capsys.readouterr()
    assert "Unauthorized. Use `croud login` to login to CrateDB Cloud." in err


def test_send_new_token_response(client: Client):
    with mock.patch("croud.api.Configuration.set_token") as set_token_mock:
        client.get("/new-token")
    assert ("session", "new-token") in client.session.cookies.items()
    assert client._token == "new-token"
    set_token_mock.assert_called_once_with("new-token", "local")


# If ``sudo=True``, the X-Auth-Sudo header should be set with any value. This
# test checks that the header is set.
def test_send_sudo_header_set(client: Client):
    client = Client(env="dev", region="bregenz.a1", sudo=True, _verify_ssl=False)
    resp_data, errors = client.get("/test-x-sudo")
    assert resp_data == {}
    assert errors is None


# If ``sudo=False``, no X-Auth-Sudo header should be set. This test checks that
# the header is not set.
def test_send_sudo_header_not_set(client: Client):
    client = Client(env="dev", region="bregenz.a1", sudo=False, _verify_ssl=False)
    resp_data, errors = client.get("/test-x-sudo")
    assert resp_data == {"message": "Header not set, as expected."}
    assert errors is None


# This test makes sure that the client is instantiated with the correct arguments,
# and does not fail if the arguments are in a random positional order.
def test_client_initialization(client: Client):
    args = argparse.Namespace(
        output_fmt="json", sudo=True, region="bregenz.a1", env="dev"
    )
    client = Client.from_args(args)
    assert client.env == "dev"
    assert client.region == "bregenz.a1"
    assert client.sudo is True


@mock.patch("croud.api.Configuration.get_token", return_value="some-token")
@mock.patch(
    "croud.api.construct_api_base_url", return_value="https://invalid.cratedb.local"
)
def test_error_message_on_connection_error(mock_construct_api_base_url, mock_get_token):
    expected_message_re = re.compile(
        r"^Failed to perform command on https://invalid\.cratedb\.local/me\. "
        r"Original error was: 'HTTPSConnectionPool\(.*\)' "
        r"Does the environment exist in the region you specified\?$"
    )
    client = Client(env="dev", region="bregenz.a1", _verify_ssl=False)
    resp_data, errors = client.get("/me")
    assert resp_data is None
    assert expected_message_re.match(errors["message"]) is not None
    assert errors["success"] is False


@pytest.mark.parametrize(
    "env,region,expected",
    [
        ("dev", "bregenz.a1", "https://bregenz.a1.cratedb-dev.cloud"),
        ("dev", "eastus.azure", "https://eastus.azure.cratedb-dev.cloud"),
        ("prod", "eastus.azure", "https://eastus.azure.cratedb.cloud"),
        ("prod", "westeurope.azure", "https://westeurope.azure.cratedb.cloud"),
    ],
)
def test_construct_api_base_url(env, region, expected):
    assert construct_api_base_url(env, region) == expected
