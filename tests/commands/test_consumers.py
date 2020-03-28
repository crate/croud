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

from croud.api import Client, RequestMethod
from tests.util import assert_rest, call_command, gen_uuid

pytestmark = pytest.mark.usefixtures("config")

eventhub_dsn = "Endpoint=sb://myhub.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=..."  # noqa
storage_dsn = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"  # noqa


@mock.patch.object(Client, "request", return_value=["data", "errors"])
def test_consumers_deploy(mock_request):
    project_id = gen_uuid()
    cluster_id = gen_uuid()

    call_command(
        "croud",
        "consumers",
        "deploy",
        "--product-name",
        "eventhub-consumer",
        "--tier",
        "S0",
        "--num-instances",
        "2",
        "--project-id",
        project_id,
        "--cluster-id",
        cluster_id,
        "--consumer-name",
        "my-eventhub-consumer",
        "--consumer-table",
        "raw",
        "--consumer-schema",
        "doc",
        "--eventhub-dsn",
        eventhub_dsn,
        "--eventhub-consumer-group",
        "$Default",
        "--lease-storage-dsn",
        storage_dsn,
        "--lease-storage-container",
        "lease_container",
    )

    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/consumers/",
        body={
            "cluster_id": cluster_id,
            "config": {
                "connection_string": eventhub_dsn,
                "consumer_group": "$Default",
                "lease_storage_connection_string": storage_dsn,
                "consumer_lease_container": "lease_container",
            },
            "instances": 2,
            "name": "my-eventhub-consumer",
            "product_name": "eventhub-consumer",
            "product_tier": "S0",
            "project_id": project_id,
            "table_name": "raw",
            "table_schema": "doc",
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_consumers_list(mock_request):
    call_command("croud", "consumers", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/consumers/", params={})


@mock.patch.object(Client, "request", return_value=({}, None))
def test_consumers_list_with_params(mock_request):
    project_id = gen_uuid()
    cluster_id = gen_uuid()
    call_command(
        "croud",
        "consumers",
        "list",
        "--project-id",
        project_id,
        "--cluster-id",
        cluster_id,
        "--product-name",
        "eventhub-consumer",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/consumers/",
        params={
            "product_name": "eventhub-consumer",
            "project_id": project_id,
            "cluster_id": cluster_id,
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_consumers_edit(mock_request):
    consumer_id = gen_uuid()
    cluster_id = gen_uuid()

    call_command(
        "croud",
        "consumers",
        "edit",
        "--consumer-id",
        consumer_id,
        "--eventhub-dsn",
        eventhub_dsn,
        "--eventhub-consumer-group",
        "$Default",
        "--lease-storage-dsn",
        storage_dsn,
        "--lease-storage-container",
        "lease_container",
        "--consumer-schema",
        "doc",
        "--consumer-table",
        "raw",
        "--cluster-id",
        cluster_id,
    )

    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        f"/api/v2/consumers/{consumer_id}/",
        body={
            "cluster_id": cluster_id,
            "config": {
                "connection_string": eventhub_dsn,
                "consumer_group": "$Default",
                "lease_storage_connection_string": storage_dsn,
                "consumer_lease_container": "lease_container",
            },
            "table_name": "raw",
            "table_schema": "doc",
        },
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_consumers_delete(mock_request, capsys):
    consumer_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["YES"]) as mock_input:
        call_command("croud", "consumers", "delete", "--consumer-id", consumer_id)
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/consumers/{consumer_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the consumer? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Consumer deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_consumers_delete_flag(mock_request, capsys):
    consumer_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
        call_command("croud", "consumers", "delete", "--consumer-id", consumer_id, "-y")
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/consumers/{consumer_id}/")
    mock_input.assert_not_called()

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Consumer deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_consumers_delete_aborted(mock_request, capsys):
    consumer_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
        call_command("croud", "consumers", "delete", "--consumer-id", consumer_id)
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the consumer? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Consumer deletion cancelled." in err_output
