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

import uuid
from datetime import datetime, timedelta, timezone
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
def test_clusers_get(mock_request):
    id = str(uuid.uuid4())
    call_command("croud", "clusters", "get", id)
    assert_rest(mock_request, RequestMethod.GET, f"/api/v2/clusters/{id}/")


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


times_create_operations_called = 0


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusters_list_with_organization_id(mock_request):
    org_id = gen_uuid()
    call_command("croud", "clusters", "list", "--org-id", org_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/clusters/",
        params={},
    )


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_deploy(_mock_sleep, mock_request, status):
    project_id = gen_uuid()
    cluster_id = gen_uuid()
    subscription_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.POST:
            return {"id": cluster_id}, None
        if args[0] == RequestMethod.GET and "/projects/" in args[1]:
            return {"organization_id": "123"}, None
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_create_operations_called
            if times_create_operations_called == 0:
                times_create_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
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
        "--subscription-id",
        subscription_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/123/clusters/",
        body={
            "cluster": {
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "product_unit": 1,
                "username": "foobar",
                "channel": "stable",
            },
            "project_id": project_id,
            "subscription_id": subscription_id,
        },
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "CREATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_deploy_no_project(_mock_sleep, mock_request):
    cluster_id = gen_uuid()
    subscription_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.POST:
            return {"id": cluster_id}, None
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            global times_create_operations_called
            if times_create_operations_called == 0:
                times_create_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": "SUCCEEDED"}]}, None
        return None, None

    mock_request.side_effect = mock_call
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
        "--cluster-name",
        "crate_cluster",
        "--version",
        "3.2.5",
        "--username",
        "foobar",
        "--password",
        "s3cr3t!",
        "--subscription-id",
        subscription_id,
        "--org-id",
        "123",
        "--region",
        "some.region",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/123/clusters/",
        body={
            "cluster": {
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "product_unit": 1,
                "username": "foobar",
                "channel": "stable",
            },
            "project": {"name": "crate_cluster", "region": "some.region"},
            "subscription_id": subscription_id,
        },
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "CREATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_clusters_deploy_fails(mock_request, capsys):
    project_id = gen_uuid()
    subscription_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/projects/" in args[1]:
            return {"organization_id": "123"}, None
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
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
        "--subscription-id",
        subscription_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/123/clusters/",
        body={
            "cluster": {
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "product_unit": 1,
                "username": "foobar",
                "channel": "stable",
            },
            "project_id": project_id,
            "subscription_id": subscription_id,
        },
        any_times=True,
    )
    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


@pytest.mark.parametrize(
    "additional_args", [[], ["--org-id", "123"], ["--region", "region"]]
)
def test_clusters_deploy_missing_args(additional_args, capsys):
    args = [
        "croud",
        "clusters",
        "deploy",
        "--product-name",
        "cratedb.az1",
        "--tier",
        "xs",
        "--unit",
        "1",
        "--cluster-name",
        "crate_cluster",
        "--version",
        "3.2.5",
        "--username",
        "foobar",
        "--password",
        "s3cr3t!",
        "--subscription-id",
        "123",
    ]
    call_command(*(args + additional_args))
    _, err_output = capsys.readouterr()
    assert (
        "Either a project id or organization id and region are required." in err_output
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_edge(_mock_sleep, mock_request):
    project_id = gen_uuid()
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.POST:
            return {"id": cluster_id}, None
        if args[0] == RequestMethod.GET and "/projects/" in args[1]:
            return {"organization_id": "123"}, None
        return None, None

    mock_request.side_effect = mock_call
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
        "--cpus",
        "1",
        "--disks",
        "1",
        "--disk-size-gb",
        "100",
        "--disk-type",
        "premium",
        "--memory-size-mb",
        "2048",
        "--subscription-id",
        "123",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/projects/{project_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/123/clusters/",
        body={
            "cluster": {
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "product_unit": 1,
                "username": "foobar",
                "channel": "stable",
                "hardware_specs": {
                    "cpus_per_node": 1.0,
                    "disks_per_node": 1,
                    "disk_size_per_node_bytes": 107_374_182_400,
                    "disk_type": "premium",
                    "memory_per_node_bytes": 2_147_483_648,
                },
            },
            "project_id": project_id,
            "subscription_id": "123",
        },
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "CREATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_deploy_no_unit(_mock_sleep, mock_request):
    project_id = gen_uuid()
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.POST:
            return {"id": cluster_id}, None
        if args[0] == RequestMethod.GET and "/projects/" in args[1]:
            return {"organization_id": "123"}, None
        return None, None

    mock_request.side_effect = mock_call
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
        "--subscription-id",
        "123",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/projects/{project_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/123/clusters/",
        body={
            "cluster": {
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "username": "foobar",
                "channel": "stable",
            },
            "project_id": project_id,
            "subscription_id": "123",
        },
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "CREATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_deploy_nightly(_mock_sleep, mock_request):
    project_id = gen_uuid()
    cluster_id = gen_uuid()
    subscription_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.POST:
            return {"id": cluster_id}, None
        if args[0] == RequestMethod.GET and "/projects/" in args[1]:
            return {"organization_id": "123"}, None
        return None, None

    mock_request.side_effect = mock_call
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
        "--subscription-id",
        subscription_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/123/clusters/",
        body={
            "cluster": {
                "crate_version": "nightly-4.1.0-20190712",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "username": "foobar",
                "channel": "nightly",
                "product_unit": 1,
            },
            "project_id": project_id,
            "subscription_id": subscription_id,
        },
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "CREATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


times_scale_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_scale(_mock_sleep, mock_request: mock.Mock, status):
    unit = 1
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_scale_operations_called

            if times_scale_operations_called == 0:
                times_scale_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
    call_command(
        "croud", "clusters", "scale", "--cluster-id", cluster_id, "--unit", str(unit)
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/scale/",
        body={"product_unit": unit},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "SCALE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_cluster_scale_fails(mock_request, capsys):
    unit = 1
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud", "clusters", "scale", "--cluster-id", cluster_id, "--unit", str(unit)
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/scale/",
        body={"product_unit": unit},
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


times_upgrade_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_upgrade(_mock_sleep, mock_request: mock.Mock, status):
    version = "3.2.6"
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_upgrade_operations_called
            if times_upgrade_operations_called == 0:
                times_upgrade_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
    call_command(
        "croud", "clusters", "upgrade", "--cluster-id", cluster_id, "--version", version
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/upgrade/",
        body={"crate_version": version},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "UPGRADE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_cluster_upgrade_fails(mock_request, capsys):
    version = "3.2.6"
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud", "clusters", "upgrade", "--cluster-id", cluster_id, "--version", version
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/upgrade/",
        body={"crate_version": version},
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


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


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusters_restart_node(mock_request):
    ordinal = 1
    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "restart-node",
        "--cluster-id",
        cluster_id,
        "--ordinal",
        str(ordinal),
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/clusters/{cluster_id}/nodes/{ordinal}",
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusters_set_deletion_protection(mock_request):
    deletion_protected = True
    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "set-deletion-protection",
        "--cluster-id",
        cluster_id,
        "--value",
        str(deletion_protected).lower(),
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/deletion-protection/",
        body={"deletion_protected": deletion_protected},
    )


times_cidr_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_set_ip_whitelist(_mock_sleep, mock_request, status):
    cidr = "8.8.8.8/32,4.4.4.4/32"
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_cidr_operations_called
            if times_cidr_operations_called == 0:
                times_cidr_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call

    with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
        call_command(
            "croud",
            "clusters",
            "set-ip-whitelist",
            "--cluster-id",
            cluster_id,
            "--net",
            cidr,
        )
    mock_input.assert_called_once_with(
        "This will overwrite all existing CIDR restrictions. Continue? [yN] "
    )

    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/ip-restrictions/",
        body={"ip_whitelist": [{"cidr": "8.8.8.8/32"}, {"cidr": "4.4.4.4/32"}]},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "ALLOWED_CIDR_UPDATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


times_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_reset_ip_whitelist(_mock_sleep, mock_request, status):
    cidr = ""
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_operations_called
            if times_operations_called == 0:
                times_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call

    call_command(
        "croud",
        "clusters",
        "set-ip-whitelist",
        "--cluster-id",
        cluster_id,
        "--net",
        cidr,
        "-y",
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/ip-restrictions/",
        body={"ip_whitelist": []},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "ALLOWED_CIDR_UPDATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_clusters_reset_ip_whitelist_fails(mock_request, capsys):
    cidr = "8.8.8.8/32,4.4.4.4/32"
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-ip-whitelist",
        "--cluster-id",
        cluster_id,
        "--net",
        cidr,
        "-y",
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/ip-restrictions/",
        body={"ip_whitelist": [{"cidr": "8.8.8.8/32"}, {"cidr": "4.4.4.4/32"}]},
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


times_expand_storage_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_expand_storage(_mock_sleep, mock_request: mock.Mock, status):
    disk_size_gb = 256
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_expand_storage_operations_called

            if times_expand_storage_operations_called == 0:
                times_expand_storage_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "expand-storage",
        "--cluster-id",
        cluster_id,
        "--disk-size-gb",
        str(disk_size_gb),
    )
    print("requests ", mock_request.call_args_list)
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/storage/",
        body={"disk_size_per_node_bytes": disk_size_gb * 1024 * 1024 * 1024},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "EXPAND_STORAGE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_cluster_expand_storage_fails(mock_request, capsys):
    disk_size_gb = 256
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "expand-storage",
        "--cluster-id",
        cluster_id,
        "--disk-size-gb",
        str(disk_size_gb),
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/storage/",
        body={"disk_size_per_node_bytes": disk_size_gb * 1024 * 1024 * 1024},
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


times_change_product_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_change_product(_mock_sleep, mock_request: mock.Mock, status):
    product_name = "cr2"
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_change_product_operations_called

            if times_change_product_operations_called == 0:
                times_change_product_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-product",
        "--cluster-id",
        cluster_id,
        "--product-name",
        product_name,
    )
    print("requests ", mock_request.call_args_list)
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/product/",
        body={"product_name": product_name},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "CHANGE_COMPUTE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_clusters_change_product_fails(mock_request, capsys):
    product_name = "cr2"
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-product",
        "--cluster-id",
        cluster_id,
        "--product-name",
        product_name,
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/product/",
        body={"product_name": product_name},
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


times_change_backup_schedule_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED"])
@pytest.mark.parametrize("backup_hours", ["12", "4,5,6", "4-8"])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_change_backup_schedule(
    _mock_time, mock_request: mock.Mock, backup_hours, status
):
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            global times_change_backup_schedule_called

            if times_change_backup_schedule_called == 0:
                times_change_backup_schedule_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-backup-schedule",
        "--cluster-id",
        cluster_id,
        "--backup-hours",
        backup_hours,
    )
    print("requests ", mock_request.call_args_list)
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/backup-schedule/",
        body={"backup_hours": backup_hours},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "BACKUP_SCHEDULE_UPDATE", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_clusters_change_backup_schedule_fails(mock_request: mock.Mock, capsys):
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-backup-schedule",
        "--cluster-id",
        cluster_id,
        "--backup-hours",
        "1,2,3,4",
    )
    print("requests ", mock_request.call_args_list)
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/backup-schedule/",
        body={"backup_hours": "1,2,3,4"},
        any_times=True,
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


times_suspend_operations_called = 0


@pytest.mark.parametrize("status", ["SUCCEEDED", "FAILED", None])
@mock.patch.object(Client, "request", return_value=({}, None))
@mock.patch("time.sleep")
def test_clusters_suspend(_mock_sleep, mock_request: mock.Mock, status):
    suspended = True
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            if status is None:
                return None, None
            global times_suspend_operations_called

            if times_suspend_operations_called == 0:
                times_suspend_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": status}]}, None
        return None, None

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-suspended-state",
        "--cluster-id",
        cluster_id,
        "--value",
        str(suspended).lower(),
    )
    print("requests ", mock_request.call_args_list)
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/suspend/",
        body={"suspended": suspended},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "SUSPEND", "limit": 1},
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_cluster_suspended_fails(mock_request, capsys):
    suspended = True
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        return None, {"message": "Some Error"}

    mock_request.side_effect = mock_call
    call_command(
        "croud",
        "clusters",
        "set-suspended-state",
        "--cluster-id",
        cluster_id,
        "--value",
        str(suspended).lower(),
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/clusters/{cluster_id}/suspend/",
        body={"suspended": suspended},
    )

    _, err_output = capsys.readouterr()
    assert "Some Error" in err_output


@pytest.mark.freeze_time("2023-01-02 00:00:00.00+00:00")
@mock.patch.object(
    Client,
    "request",
    return_value=(
        [
            {
                "cluster_id": "some",
                "concrete_indices": ["nyc_taxi"],
                "created": "2023-01-01T08:39:13.451000+00:00",
                "dc": {
                    "created": "2023-01-01T08:39:22.508000+00:00",
                    "modified": "2023-01-01T08:39:22.508000+00:00",
                },
                "project_id": "other",
                "repository": "system_backup_20220804103901",
                "snapshot": "20230101083912",
                "tables": ["doc.nyc_taxi"],
            }
        ],
        {},
    ),
)
def test_cluster_snapshots_list(mock_request, capsys):
    cluster_id = gen_uuid()

    call_command(
        "croud",
        "clusters",
        "snapshots",
        "list",
        "--cluster-id",
        cluster_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/snapshots/",
        params={"start": "2022-12-31T00:00:00+00:00"},
    )
    stdout, _ = capsys.readouterr()
    assert "2023-01-01T08:39:13.451000+00:00" in stdout
    assert "system_backup_20220804103901" in stdout
    assert "20230101083912" in stdout


@pytest.mark.freeze_time("2023-01-02 00:00:00.00+00:00")
@pytest.mark.parametrize("days", [None, 1, 14, 365])
@mock.patch.object(Client, "request", return_value=([], {}))
def test_cluster_snapshots_list_no_backups(mock_request, days, capsys):
    cluster_id = gen_uuid()
    args = ["croud", "clusters", "snapshots", "list", "--cluster-id", cluster_id]
    if days:
        args.append("--days-ago")
        args.append(f"{days}")

    call_command(*args)
    expected_days = 2 if not days else days
    start = datetime.now(tz=timezone.utc) - timedelta(days=expected_days)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/snapshots/",
        params={"start": start.isoformat()},
    )
    _, stderr = capsys.readouterr()
    assert (
        f"Looks like there are no snapshots for the last {expected_days} days" in stderr
    )


def test_cluster_snapshots_restore_missing_repository(capsys):
    cluster_id = gen_uuid()

    with pytest.raises(SystemExit) as e_info:
        call_command(
            "croud",
            "clusters",
            "snapshots",
            "restore",
            "--cluster-id",
            cluster_id,
            "--snapshot",
            "the-snapshot",
        )

        output, err_output = capsys.readouterr()
        assert "The following arguments are required: --repository" in err_output
        assert e_info.value.code == 1


times_restore_operations_called = 0


@mock.patch.object(Client, "request")
@mock.patch("time.sleep")
def test_cluster_snapshots_restore(_mock_sleep, mock_request):
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            global times_restore_operations_called

            if times_restore_operations_called == 0:
                times_restore_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": "SUCCEEDED"}]}, None
        return None, {}

    mock_request.side_effect = mock_call

    body = {
        "snapshot": "the-snapshot-name",
        "repository": "a-repository",
        "type": "all",
    }

    call_command(
        "croud",
        "clusters",
        "snapshots",
        "restore",
        "--cluster-id",
        cluster_id,
        "--repository",
        body["repository"],
        "--snapshot",
        body["snapshot"],
        "--type",
        body["type"],
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/snapshots/restore/",
        body=body,
        any_times=True,
    )

    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "RESTORE_SNAPSHOT", "limit": 1},
        any_times=True,
    )
    assert mock_request.call_count == 3


times_opt_restore_operations_called = 0


@mock.patch.object(Client, "request")
@mock.patch("time.sleep")
def test_cluster_snapshots_restore_with_optional_params(_mock_sleep, mock_request):
    cluster_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/operations/" in args[1]:
            global times_opt_restore_operations_called

            if times_opt_restore_operations_called == 0:
                times_opt_restore_operations_called += 1
                return {"operations": [{"status": "SENT"}]}, None
            return {"operations": [{"status": "SUCCEEDED"}]}, None
        return None, {}

    mock_request.side_effect = mock_call

    body = {
        "snapshot": "the-snapshot-name",
        "repository": "a-repository",
        "source_cluster_id": "another-cluster-id",
        "type": "tables",
        "tables": ["table1", "table2"],
    }

    call_command(
        "croud",
        "clusters",
        "snapshots",
        "restore",
        "--cluster-id",
        cluster_id,
        "--repository",
        body["repository"],
        "--snapshot",
        body["snapshot"],
        "--source-cluster-id",
        body["source_cluster_id"],
        "--type",
        "tables",
        "--tables",
        " table1 , table2 ",  # Ensure the parameter is properly trimmed
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/snapshots/restore/",
        body=body,
        any_times=True,
    )

    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/operations/",
        params={"type": "RESTORE_SNAPSHOT", "limit": 1},
        any_times=True,
    )

    assert mock_request.call_count == 3


@mock.patch.object(Client, "request", return_value=({}, None))
def test_import_job_delete(mock_request):
    cluster_id = gen_uuid()
    import_job_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "import-jobs",
        "delete",
        "--import-job-id",
        import_job_id,
        "--cluster-id",
        cluster_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/clusters/{cluster_id}/import-jobs/{import_job_id}/",
    )


@mock.patch.object(
    Client, "request", return_value=({"id": "1", "status": "SUCCEEDED"}, None)
)
def test_import_job_create_from_url(mock_request):
    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "import-jobs",
        "create",
        "from-url",
        "--cluster-id",
        cluster_id,
        "--url",
        "http://download-url.com/csv-file.csv.gz",
        "--file-format",
        "csv",
        "--compression",
        "gzip",
        "--table",
        "my-table",
        "--create-table",
        "false",
    )
    body = {
        "type": "url",
        "url": {
            "url": "http://download-url.com/csv-file.csv.gz",
        },
        "format": "csv",
        "destination": {"table": "my-table", "create_table": False},
        "compression": "gzip",
    }
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/import-jobs/",
        body=body,
        any_times=True,
    )


@mock.patch.object(
    Client, "request", return_value=({"id": "1", "status": "SUCCEEDED"}, None)
)
def test_import_job_create_from_s3(mock_request):
    cluster_id = gen_uuid()
    bucket = "my-bucket-name"
    file_path = "my-folder/my-file.csv.gz"
    secret_id = gen_uuid()
    endpoint = "https://my-s3-compatible-endpoint"
    call_command(
        "croud",
        "clusters",
        "import-jobs",
        "create",
        "from-s3",
        "--cluster-id",
        cluster_id,
        "--bucket",
        bucket,
        "--file-path",
        file_path,
        "--secret-id",
        secret_id,
        "--endpoint",
        endpoint,
        "--compression",
        "gzip",
        "--file-format",
        "csv",
        "--table",
        "my-table",
        "--create-table",
        "false",
    )
    body = {
        "type": "s3",
        "s3": {
            "bucket": bucket,
            "file_path": file_path,
            "secret_id": secret_id,
            "endpoint": endpoint,
        },
        "format": "csv",
        "destination": {"table": "my-table", "create_table": False},
        "compression": "gzip",
    }
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/import-jobs/",
        body=body,
        any_times=True,
    )


@mock.patch.object(
    Client, "request", return_value=({"id": "1", "status": "SUCCEEDED"}, None)
)
def test_import_job_create_from_file(mock_request):
    cluster_id = gen_uuid()
    file_uuid = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "import-jobs",
        "create",
        "from-file",
        "--cluster-id",
        cluster_id,
        "--file-id",
        file_uuid,
        "--file-format",
        "csv",
        "--compression",
        "gzip",
        "--table",
        "my-table",
        "--create-table",
        "false",
    )
    body = {
        "type": "file",
        "file": {
            "id": file_uuid,
        },
        "format": "csv",
        "destination": {"table": "my-table", "create_table": False},
        "compression": "gzip",
    }
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/import-jobs/",
        body=body,
        any_times=True,
    )


@mock.patch.object(
    Client, "request", return_value=({"id": "1", "status": "SUCCEEDED"}, None)
)
def test_import_job_create_from_azure_blob_storage(mock_request):
    cluster_id = gen_uuid()
    secret_id = gen_uuid()
    container_name = "my-container-name"
    blob_name = "path/to/my/files/*.csv.gz"

    call_command(
        "croud",
        "clusters",
        "import-jobs",
        "create",
        "from-azure-blob-storage",
        "--cluster-id",
        cluster_id,
        "--file-format",
        "csv",
        "--compression",
        "gzip",
        "--table",
        "my-table",
        "--create-table",
        "false",
        "--container-name",
        container_name,
        "--blob-name",
        blob_name,
        "--secret-id",
        secret_id,
    )
    body = {
        "type": "azureblob",
        "azureblob": {
            "container_name": container_name,
            "blob_name": blob_name,
            "secret_id": secret_id,
        },
        "format": "csv",
        "destination": {"table": "my-table", "create_table": False},
        "compression": "gzip",
    }
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/import-jobs/",
        body=body,
        any_times=True,
    )


@mock.patch.object(
    Client,
    "request",
    return_value=(
        [
            {
                "cluster_id": "123",
                "compression": "gzip",
                "dc": {
                    "created": "2023-03-14T10:12:29.763000+00:00",
                    "modified": "2023-03-14T10:12:29.763000+00:00",
                },
                "destination": {"create_table": True, "table": "croud-csv-import-two"},
                "format": "csv",
                "id": "a95e5a20-61f7-415f-b128-1e21ddf17513",
                "progress": {
                    "bytes": 0,
                    "message": "Failed",
                    "records": 0,
                },
                "status": "FAILED",
                "type": "url",
                "url": {"url": "https://some"},
            },
            {
                "cluster_id": "123",
                "compression": "gzip",
                "dc": {
                    "created": "2023-03-14T10:12:29.763000+00:00",
                    "modified": "2023-03-14T10:12:29.763000+00:00",
                },
                "destination": {"create_table": True, "table": "croud-csv-import-two"},
                "format": "json",
                "id": "a95e5a20-61f7-415f-b128-1e21ddf17513",
                "progress": {
                    "bytes": 0,
                    "message": "Failed",
                    "records": 0,
                },
                "status": "FAILED",
                "type": "s3",
                "s3": {
                    "endpoint": "https://some",
                    "file_path": "a-file-path",
                    "bucket": "bucket-name",
                    "secret_id": "a95e5a20-61f7-415f-b128-1e21ddf17513",
                },
            },
            {
                "cluster_id": "123",
                "compression": "gzip",
                "dc": {
                    "created": "2023-03-14T10:12:29.763000+00:00",
                    "modified": "2023-03-14T10:12:29.763000+00:00",
                },
                "destination": {"create_table": True, "table": "croud-csv-import-two"},
                "format": "json",
                "id": "a95e5a20-61f7-415f-b128-1e21ddf17513",
                "progress": {
                    "bytes": 0,
                    "message": "Failed",
                    "records": 0,
                },
                "status": "FAILED",
                "type": "file",
                "file": {
                    "upload_url": "https://server.test/folder/myfile.json",
                    "file_size": 36,
                    "id": "a95e5a20-61f7-415f-b128-1e21ddf17513",
                    "name": "my test file",
                    "status": "UPLOADED",
                },
            },
        ],
        None,
    ),
)
@pytest.mark.parametrize("output_format", ["table", "wide"])
def test_import_job_list(mock_request, output_format):
    call_command(
        "croud",
        "clusters",
        "import-jobs",
        "list",
        "--cluster-id",
        "123",
        "-o",
        output_format,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/clusters/123/import-jobs/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_import_job_progress_summary(mock_request):
    cluster_id = gen_uuid()
    import_job_id = gen_uuid()

    args = [
        "croud",
        "clusters",
        "import-jobs",
        "progress",
        "--summary",
        "true",
        "--cluster-id",
        cluster_id,
        "--import-job-id",
        import_job_id,
    ]

    call_command(*args)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/import-jobs/{import_job_id}/progress/",
        params={},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@pytest.mark.parametrize(
    "params", [{}, {"offset": 2}, {"limit": "2"}, {"limit": "ALL", "offset": 2}]
)
def test_import_job_progress_files(mock_request, params):
    cluster_id = gen_uuid()
    import_job_id = gen_uuid()

    args = [
        "croud",
        "clusters",
        "import-jobs",
        "progress",
        "--cluster-id",
        cluster_id,
        "--import-job-id",
        import_job_id,
    ]
    for param_key, param_value in params.items():
        args.append(f"--{param_key}")
        args.append(f"{param_value}")

    call_command(*args)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/import-jobs/{import_job_id}/progress/",
        params=params,
    )


@mock.patch.object(
    Client,
    "request",
    return_value=(
        [
            {
                "cluster_id": "12345",
                "dc": {
                    "created": "2023-07-04T10:12:29.763000+00:00",
                    "modified": "2023-07-04T10:12:29.763000+00:00",
                },
                "source": {"table": "my_table"},
                "destination": {"format": "csv", "file": {"id": ""}},
                "id": "45678",
                "progress": {
                    "bytes": 0,
                    "message": "Failed",
                    "records": 0,
                },
                "status": "FAILED",
            }
        ],
        None,
    ),
)
def test_export_job_list(mock_request):
    cluster_id = gen_uuid()
    call_command("croud", "clusters", "export-jobs", "list", "--cluster-id", cluster_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/export-jobs/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_export_job_delete(mock_request):
    cluster_id = gen_uuid()
    export_job_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "export-jobs",
        "delete",
        "--export-job-id",
        export_job_id,
        "--cluster-id",
        cluster_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/clusters/{cluster_id}/export-jobs/{export_job_id}/",
    )


@pytest.mark.parametrize("save_file", [True, False])
@mock.patch("croud.clusters.commands.copyfileobj")
@mock.patch.object(Client, "request")
def test_export_job_create(mock_client_request, mock_copy, save_file):
    cluster_id = gen_uuid()
    project_id = gen_uuid()
    org_id = gen_uuid()
    file_id = gen_uuid()
    export_job_id = gen_uuid()
    mock_client_request.side_effect = [
        (
            {
                "id": export_job_id,
                "status": "IN_PROGRESS",
                "progress": {"message": "Export in progress."},
            },
            None,
        ),
        (
            {
                "id": export_job_id,
                "status": "SUCCEEDED",
                "destination": {"file": {"id": file_id}},
                "progress": {
                    "message": "Export finished successfully.",
                    "records": 123,
                    "bytes": 456,
                },
            },
            None,
        ),
        (
            {
                "id": export_job_id,
                "status": "SUCCEEDED",
                "destination": {"file": {"id": file_id}},
                "progress": {
                    "message": "Export finished successfully.",
                    "records": 123,
                    "bytes": 456,
                },
            },
            None,
        ),
        ({"project_id": project_id}, None),
        ({"organization_id": org_id}, None),
        (
            {"download_url": "https://s3-presigned-url.s3.amazonaws.com/some/bla"},
            None,
        ),
    ]

    cluster_id = gen_uuid()

    mock_response = mock.MagicMock()
    mock_response.headers = {"Content-Length": 123}
    mock_response.status_code = 200

    with mock.patch("requests.get", return_value=mock_response):
        with mock.patch("builtins.open", mock.mock_open(read_data="id,name,path")):
            cmd = (
                "croud",
                "clusters",
                "export-jobs",
                "create",
                "--cluster-id",
                cluster_id,
                "--file-format",
                "csv",
                "--table",
                "my-table",
                "--compression",
                "gzip",
            )
            if save_file:
                cmd = cmd + (
                    "--save-as",
                    "./my_table.csv",
                )
            call_command(*cmd)

    body = {
        "source": {
            "table": "my-table",
        },
        "destination": {"format": "csv"},
        "compression": "gzip",
    }
    assert_rest(
        mock_client_request,
        RequestMethod.POST,
        f"/api/v2/clusters/{cluster_id}/export-jobs/",
        body=body,
        any_times=True,
    )
    assert_rest(
        mock_client_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/export-jobs/{export_job_id}/",
        any_times=True,
    )
    assert_rest(
        mock_client_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )
    assert_rest(
        mock_client_request,
        RequestMethod.GET,
        f"/api/v2/projects/{project_id}/",
        any_times=True,
    )
    assert_rest(
        mock_client_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/files/{file_id}/",
        any_times=True,
    )
    if save_file:
        mock_copy.assert_called_once()
    else:
        mock_copy.assert_not_called()
