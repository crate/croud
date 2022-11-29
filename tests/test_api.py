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
from platform import python_version

import pytest

import croud
from croud.api import Client


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
    assert errors == {"message": "500 - Internal Server Error", "success": False}


def test_send_empty_response(client: Client):
    resp_data, errors = client.get("/empty-response")
    assert resp_data is None
    assert errors is None


def test_send_redirect_response(client: Client, capsys):
    with pytest.raises(SystemExit):
        client.get("/redirect")
    _, err = capsys.readouterr()
    assert "Unauthorized." in err
    assert "Use `croud login` to login to CrateDB Cloud." in err


def test_send_new_token_response(client: Client, config):
    client.get("/new-token")
    assert ("session", "new-token") in client.session.cookies.items()
    assert config.token == client._token == "new-token"


@pytest.mark.parametrize("sudo", [True, False])
def test_send_sudo_header(sudo, config):
    client = Client(config.endpoint, region="bregenz.a1", sudo=sudo, _verify_ssl=False)
    resp_data, errors = client.get("/client-headers")
    assert ("X-Auth-Sudo" in resp_data) == sudo  # type: ignore


def test_send_user_agent_header(config):
    client = Client(config.endpoint, region="bregenz.a1", _verify_ssl=False)
    resp_data, errors = client.get("/client-headers")
    expected_ua = f"Croud/{croud.__version__} Python/{python_version()}"
    assert resp_data["User-Agent"] == expected_ua


@pytest.mark.parametrize(
    "argument,is_header_present", [(None, False), ("westeurope.azure", True)]
)
def test_send_region_header(argument, is_header_present, config):
    client = Client(config.endpoint, region=argument, _verify_ssl=False)
    resp_data, errors = client.get("/client-headers")
    if is_header_present:
        assert resp_data["X-Region"] == argument  # type: ignore
    else:
        assert "X-Region" not in resp_data


def test_client_initialization(config):
    args = argparse.Namespace(sudo=True, region="bregenz.a1")
    client = Client.from_args(args)
    assert str(client.base_url) == config.endpoint
    assert client.session.headers["X-Region"] == "bregenz.a1"
    assert client.session.headers["X-Auth-Sudo"] == "1"
    assert client.session.cookies["session"] == config.token


def test_error_message_on_connection_error(config):
    config.add_profile("test", endpoint="https://invalid.cratedb.local")
    config.set_auth_token("test", "some-token")
    config.use_profile("test")

    expected_message_re = re.compile(
        r"^Failed to perform request on 'https://invalid\.cratedb\.local/me\'. "
        r"Original error was: '.*'$"
    )
    client = Client(config.endpoint, _verify_ssl=False)
    resp_data, errors = client.get("/me")
    print(resp_data, errors)
    assert resp_data is None
    assert expected_message_re.match(errors["message"]) is not None
    assert errors["success"] is False


def test_auth_with_key_and_secret(config):
    client = Client(
        config.endpoint, key="some-key", secret="some-secret", _verify_ssl=False
    )
    resp_data, errors = client.get("/client-headers")
    assert resp_data["Authorization"] == "Basic c29tZS1rZXk6c29tZS1zZWNyZXQ="
