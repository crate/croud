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
        "change-product",
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
        "change-product",
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
