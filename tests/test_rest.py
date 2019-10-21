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

import pytest

from croud.config import Configuration
from croud.rest import Client
from croud.session import RequestMethod


@pytest.fixture
def client(fake_cloud_connector, event_loop):
    with mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx"):
        yield Client(
            env="dev", region="bregenz.a1", conn=fake_cloud_connector, loop=event_loop
        )


@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_success_sets_data_with_key(mock_cloud_url, client):
    resp_data, errors = client.send(RequestMethod.GET, "/data/data-key")
    assert resp_data["data"] == {"key": "value"}
    assert errors is None


@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_success_sets_data_without_key(mock_cloud_url, client):
    resp_data, errors = client.send(RequestMethod.GET, "/data/no-key")
    assert resp_data == {"key": "value"}
    assert errors is None


@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_error_sets_error(mock_cloud_url, client):
    resp_data, errors = client.send(RequestMethod.GET, "/errors/400")
    assert errors == {"message": "Bad request.", "errors": {"key": "Error on 'key'"}}


@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_text_response(mock_cloud_url, client):
    resp_data, errors = client.send(RequestMethod.GET, "/text-response")
    assert resp_data is None
    assert errors == {"message": "Invalid response type.", "success": False}


@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_empty_response(mock_cloud_url, client):
    resp_data, errors = client.send(RequestMethod.GET, "/empty-response")
    assert resp_data is None
    assert errors is None


# If ``sudo=True``, the X-Auth-Sudo header should be set with any value. This
# test checks that the header is set.
@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_sudo_header_set(
    mock_cloud_url, mock_token, fake_cloud_connector, event_loop
):
    client = Client(
        env="dev",
        region="bregenz.a1",
        sudo=True,
        conn=fake_cloud_connector,
        loop=event_loop,
    )
    resp_data, errors = client.send(RequestMethod.GET, f"/test-x-sudo")
    assert resp_data == {}
    assert errors is None


# If ``sudo=False``, no X-Auth-Sudo header should be set. This test checks that
# the header is not set.
@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_send_sudo_header_not_set(
    mock_cloud_url, mock_token, fake_cloud_connector, event_loop
):
    client = Client(
        env="dev",
        region="bregenz.a1",
        sudo=False,
        conn=fake_cloud_connector,
        loop=event_loop,
    )
    resp_data, errors = client.send(RequestMethod.GET, f"/test-x-sudo")
    assert resp_data == {"message": "Header not set, as expected."}
    assert errors is None


# This test makes sure that the client is instantiated with the correct arguments,
# and does not fail if the arguments are in a random positional order.
@mock.patch.object(Configuration, "get_token", return_value="eyJraWQiOiIx")
@mock.patch("croud.session.cloud_url", return_value="https://cratedb.local")
def test_client_initialization(mock_cloud_url, mock_token, event_loop):
    args = argparse.Namespace(
        output_fmt="json", sudo=True, region="bregenz.a1", env="dev"
    )
    client = Client.from_args(args)
    assert client._env == "dev"
    assert client._region == "bregenz.a1"
    assert client._sudo is True
    assert isinstance(client.loop, asyncio.AbstractEventLoop)


@mock.patch("croud.session.cloud_url", return_value="https://invalid.cratedb.local")
def test_error_message_on_connection_error(mock_cloud_url, client):
    expected_message = (
        "Failed to perform command on invalid.cratedb.local. "
        "Original error was: 'Cannot connect to host invalid.cratedb.local:443 ssl:None [Name or service not known]' "  # noqa
        "Does the environment exist in the region you specified?"
    )
    resp_data, errors = client.send(RequestMethod.GET, "/me")
    assert resp_data is None
    assert errors == {"message": expected_message, "success": False}
