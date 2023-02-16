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
from croud.printer import print_raw
from tests.util import assert_rest, call_command, gen_uuid

EDGE_REGION_LIST = [
    {
        "dc": None,
        "deprecated": False,
        "description": "region-description",
        "is_edge_region": True,
        "last_seen": None,
        "name": "region-name",
        "organization_id": "organization-id",
        "status": "DOWN",
    }
]


@mock.patch.object(Client, "request", return_value=({}, None))
def test_regions_list(mock_request):
    call_command("croud", "regions", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/regions/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_regions_list_with_organization_id(mock_request):
    org_id = gen_uuid()
    call_command("croud", "regions", "list", "--org-id", org_id)
    assert_rest(
        mock_request, RequestMethod.GET, f"/api/v2/organizations/{org_id}/regions/"
    )


@mock.patch.object(Client, "request", return_value=({"name": "region-name"}, None))
def test_regions_create_all_params(mock_request):
    call_command(
        "croud",
        "regions",
        "create",
        "--description",
        "region-description",
        "--aws-bucket",
        "backup-bucket",
        "--aws-region",
        "backup-region",
        "--org-id",
        "organization-id",
        "--yes",
    )

    mock_request.call_args_list[0].assert_called_with(
        RequestMethod.POST,
        "/api/v2/regions/",
        body={
            "description": "region-description",
            "aws_bucket": "backup-bucket",
            "aws_region": "backup-region",
            "organization_id": "organization-id",
        },
        params=None,
    )
    mock_request.call_args_list[1].assert_called_with(
        RequestMethod.GET, "/api/v2/regions/region-name/install-token/", params=None
    )


@mock.patch.object(Client, "request", return_value=({"name": "region-name"}, None))
def test_regions_create_mandatory_params(mock_request):
    call_command(
        "croud",
        "regions",
        "create",
        "--description",
        "region-description",
        "--org-id",
        "organization-id",
        "--yes",
    )

    mock_request.call_args_list[0].assert_called_with(
        RequestMethod.POST,
        "/api/v2/regions/",
        body={
            "description": "region-description",
            "organization_id": "organization-id",
        },
        params=None,
    )
    mock_request.call_args_list[1].assert_called_with(
        RequestMethod.GET, "/api/v2/regions/region-name/install-token/", params=None
    )


@mock.patch("croud.regions.commands.print_raw", wraps=print_raw)
@mock.patch.object(
    Client,
    "request",
    side_effect=[({"name": "region-name"}, None), ({"token": "my-token"}, None)],
)
def test_regions_create_install_command(mock_request, mock_raw_printer, client):
    call_command(
        "croud",
        "regions",
        "create",
        "--description",
        "region-description",
        "--org-id",
        "organization-id",
        "--yes",
    )

    mock_request.call_args_list[0].assert_called_with(
        RequestMethod.POST,
        "/api/v2/regions/",
        body={
            "description": "region-description",
            "organization_id": "organization-id",
        },
        params=None,
    )
    mock_request.call_args_list[1].assert_called_with(
        RequestMethod.GET, "/api/v2/regions/region-name/install-token/", params=None
    )

    assert any(
        f"$ bash <( wget -qO- {client.base_url}/edge/cratedb-cloud-edge.sh) my-token"
        in item
        for item in mock_raw_printer.call_args[0][0]
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_regions_create_missing_description(mock_request, capsys):
    with pytest.raises(SystemExit):
        call_command(
            "croud",
            "regions",
            "create",
            "--org-id",
            "organization-id",
            "--yes",
        )
    mock_request.assert_not_called()
    _, err_output = capsys.readouterr()
    assert "The following arguments are required: --description" in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_regions_create_aborted(mock_request, capsys):
    with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
        call_command(
            "croud",
            "regions",
            "create",
            "--description",
            "region-description",
            "--org-id",
            "organization-id",
        )
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "Creating a region is an experimental feature. Are you sure you want to proceed? [yN] "  # noqa
    )

    _, err_output = capsys.readouterr()
    assert "Region creation cancelled." in err_output


@mock.patch.object(
    Client,
    "request",
    side_effect=[(EDGE_REGION_LIST, None), ({}, None)],
)
def test_regions_delete(mock_request, capsys):
    call_command(
        "croud",
        "regions",
        "delete",
        "-y",
        "--name",
        "region-name",
    )
    mock_request.assert_has_calls(
        [
            mock.call(RequestMethod.GET, "/api/v2/regions/", params=None),
            mock.call(
                RequestMethod.DELETE,
                "/api/v2/regions/region-name/",
                params=None,
                body=None,
            ),
        ]
    )


@mock.patch.object(
    Client,
    "request",
    side_effect=[
        (EDGE_REGION_LIST, None),
        (
            None,
            {
                "success": False,
                "message": "Deletion requires no resources to be related to the target.",  # noqa
                "related_resources": {
                    "projects": [
                        "5d8e1a81-e2fe-48bb-8cc2-fbdbebfe2d8f",
                        "42023d1f-462e-4130-aa82-6025342b11c5",
                    ]
                },
            },
        ),
    ],
)
def test_regions_delete_with_projects_fails(mock_request, capsys):
    call_command(
        "croud",
        "regions",
        "delete",
        "-y",
        "--name",
        "region-name",
    )
    mock_request.assert_has_calls(
        [
            mock.call(RequestMethod.GET, "/api/v2/regions/", params=None),
            mock.call(
                RequestMethod.DELETE,
                "/api/v2/regions/region-name/",
                params=None,
                body=None,
            ),
        ]
    )
    data, err_output = capsys.readouterr()
    assert "Deletion requires no resources to be related to the target." in err_output
    assert "5d8e1a81-e2fe-48bb-8cc2-fbdbebfe2d8f" in data
    assert "42023d1f-462e-4130-aa82-6025342b11c5" in data


@mock.patch.object(
    Client,
    "request",
    side_effect=[({}, None)],
)
def test_regions_delete_missing_name(mock_request, capsys):
    with pytest.raises(SystemExit):
        call_command(
            "croud",
            "regions",
            "delete",
            "-y",
        )
    mock_request.assert_not_called()
    _, err_output = capsys.readouterr()
    assert "The following arguments are required: --name" in err_output


@mock.patch.object(
    Client,
    "request",
    side_effect=[
        (
            [
                {
                    "dc": None,
                    "deprecated": False,
                    "description": "region-description",
                    "is_edge_region": True,
                    "last_seen": None,
                    "name": "region-name",
                    "organization_id": "organization-id",
                    "status": "UP",
                }
            ],
            None,
        ),
    ],
)
def test_regions_delete_status_up(mock_request, capsys, client):
    call_command("croud", "regions", "delete", "-y", "--name", "region-name")
    mock_request.assert_called_once_with(
        RequestMethod.GET,
        "/api/v2/regions/",
        params=None,
    )
    data, err_output = capsys.readouterr()
    msg = (
        "Your region is still connected to CrateDB Cloud. Please uninstall "
        "the CrateDB Edge stack from the region before deleting it by "
        "running the script below:\nbash <(wget -qO- "
        f"{client.base_url}/edge/uninstall-cratedb-cloud-edge.sh)"
    )
    assert msg in err_output


@mock.patch.object(
    Client,
    "request",
    side_effect=[(EDGE_REGION_LIST, None), ({}, None)],
)
def test_regions_delete_status_down(mock_request, capsys):
    call_command("croud", "regions", "delete", "-y", "--name", "region-name")
    mock_request.assert_has_calls(
        [
            mock.call(RequestMethod.GET, "/api/v2/regions/", params=None),
            mock.call(
                RequestMethod.DELETE,
                "/api/v2/regions/region-name/",
                params=None,
                body=None,
            ),
        ]
    )


@mock.patch.object(
    Client,
    "request",
    side_effect=[({}, None)],
)
def test_regions_delete_bad_name(mock_request, capsys):
    region_name = "region-name"

    call_command("croud", "regions", "delete", "-y", "--name", region_name)
    mock_request.assert_called_once_with(
        RequestMethod.GET,
        "/api/v2/regions/",
        params=None,
    )
    _, err_output = capsys.readouterr()
    assert f"The region {region_name} does not exist." in err_output
