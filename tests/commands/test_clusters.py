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


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_list(mock_request):
    call_command("croud", "clusters", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/clusters/", params={})


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_list_with_project_id(mock_request):
    project_id = gen_uuid()
    call_command("croud", "clusters", "list", "--project-id", project_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/clusters/",
        params={"project_id": project_id},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_deploy(mock_request):
    project_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "deploy",
        "--product-name",
        "cratedb.az1",
        "--tier",
        "xs",
        "--unit",
        "1",
        "--project-id",
        project_id,
        "--cluster-name",
        "crate_cluster",
        "--version",
        "3.2.5",
        "--username",
        "foobar",
        "--password",
        "s3cr3t!",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/clusters/",
        body={
            "crate_version": "3.2.5",
            "name": "crate_cluster",
            "password": "s3cr3t!",
            "product_name": "cratedb.az1",
            "product_tier": "xs",
            "product_unit": 1,
            "project_id": project_id,
            "username": "foobar",
            "channel": "stable",
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_deploy_no_unit(mock_request):
    project_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "deploy",
        "--product-name",
        "cratedb.az1",
        "--tier",
        "xs",
        "--project-id",
        project_id,
        "--cluster-name",
        "crate_cluster",
        "--version",
        "3.2.5",
        "--username",
        "foobar",
        "--password",
        "s3cr3t!",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/clusters/",
        body={
            "crate_version": "3.2.5",
            "name": "crate_cluster",
            "password": "s3cr3t!",
            "product_name": "cratedb.az1",
            "product_tier": "xs",
            "project_id": project_id,
            "username": "foobar",
            "channel": "stable",
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_deploy_nightly(mock_request):
    project_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "deploy",
        "--product-name",
        "cratedb.az1",
        "--tier",
        "xs",
        "--unit",
        "1",
        "--project-id",
        project_id,
        "--cluster-name",
        "crate_cluster",
        "--version",
        "nightly-4.1.0-20190712",
        "--username",
        "foobar",
        "--password",
        "s3cr3t!",
        "--channel",
        "nightly",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/clusters/",
        body={
            "crate_version": "nightly-4.1.0-20190712",
            "name": "crate_cluster",
            "password": "s3cr3t!",
            "product_name": "cratedb.az1",
            "product_tier": "xs",
            "project_id": project_id,
            "username": "foobar",
            "channel": "nightly",
            "product_unit": 1,
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_scale(mock_request):
    unit = 1
    cluster_id = gen_uuid()
    call_command(
        "croud", "clusters", "scale", "--cluster-id", cluster_id, "--unit", "1"
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/scale/",
        body={"product_unit": unit},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusers_upgrade(mock_request):
    version = "3.2.6"
    cluster_id = gen_uuid()
    call_command(
        "croud", "clusters", "upgrade", "--cluster-id", cluster_id, "--version", version
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/upgrade/",
        body={"crate_version": version},
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_clusters_delete(mock_request, capsys):
    cluster_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
        call_command("croud", "clusters", "delete", "--cluster-id", cluster_id)
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/clusters/{cluster_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the cluster? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Cluster deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_clusters_delete_flag(mock_request, capsys):
    cluster_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
        call_command("croud", "clusters", "delete", "--cluster-id", cluster_id, "-y")
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/clusters/{cluster_id}/")
    mock_input.assert_not_called()

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Cluster deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_clusters_delete_aborted(mock_request, capsys):
    cluster_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
        call_command("croud", "clusters", "delete", "--cluster-id", cluster_id)
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the cluster? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Cluster deletion cancelled." in err_output
