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
from tests.util import assert_rest, call_command


@mock.patch.object(Client, "request", return_value=({}, None))
def test_regions_list(mock_request):
    call_command("croud", "regions", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/regions/")


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
        "--provider",
        "EDGE",
        "--org-id",
        "organization-id",
        "--name",
        "region-name",
        "--yes",
    )

    mock_request.call_args_list[0].assert_called_with(
        RequestMethod.POST,
        "/api/v2/regions/",
        body={
            "description": "region-description",
            "aws_bucket": "backup-bucket",
            "aws_region": "backup-region",
            "provider": "EDGE",
            "name": "region-name",
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
        "--provider",
        "EDGE",
        "--yes",
    )

    mock_request.call_args_list[0].assert_called_with(
        RequestMethod.POST,
        "/api/v2/regions/",
        body={"description": "region-description", "provider": "EDGE"},
        params=None,
    )
    mock_request.call_args_list[1].assert_called_with(
        RequestMethod.GET, "/api/v2/regions/region-name/install-token/", params=None
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_regions_create_missing_description(mock_request, capsys):
    with pytest.raises(SystemExit):
        call_command(
            "croud", "regions", "create", "--provider", "EDGE", "--yes",
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
            "--provider",
            "EDGE",
        )
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "The creation of a region is an experimental feature. Do you really want to use it? [yN] "  # noqa
    )

    _, err_output = capsys.readouterr()
    assert "Region creation cancelled." in err_output


@mock.patch.object(Client, "request", return_value=({}, None))
def test_get_region_deployment_manifest(mock_request):
    call_command(
        "croud",
        "regions",
        "generate-deployment-manifest",
        "--region-name",
        "region-name",
        "--yes",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/regions/region-name/deployment-manifest/",
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_get_region_deployment_manifest_aborted(mock_request, capsys):
    with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
        call_command(
            "croud",
            "regions",
            "generate-deployment-manifest",
            "--region-name",
            "region-name",
        )
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "The generation of a deployment manfiest for an edge region is an experimental feature. Do you really want to use it? [yN] "  # noqa
    )

    _, err_output = capsys.readouterr()
    assert "Deployment manifest generation cancelled." in err_output
