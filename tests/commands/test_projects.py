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
from croud.projects.users.commands import (
    role_fqn_transform as project_role_fqn_transform,
)
from tests.util import assert_rest, call_command, gen_uuid

pytestmark = pytest.mark.usefixtures("config")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_projects_create(mock_request):
    call_command(
        "croud",
        "projects",
        "create",
        "--name",
        "new-project",
        "--org-id",
        "organization-id",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/projects/",
        body={"name": "new-project", "organization_id": "organization-id"},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_projects_create_with_custom_backup(mock_request):
    call_command(
        "croud",
        "projects",
        "create",
        "--name",
        "new-project",
        "--org-id",
        "organization-id",
        "--backup-location",
        "some",
        "--backup-location-type",
        "s3",
        "--backup-location-access-key-id",
        "123",
        "--backup-location-secret-access-key",
        "321",
        "--backup-location-endpoint-url",
        "https://minio.svc.local",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/projects/",
        body={
            "name": "new-project",
            "organization_id": "organization-id",
            "backup_location": {
                "location_type": "s3",
                "location": "some",
                "credentials": {"access_key_id": "123", "secret_access_key": "321"},
                "additional_config": {"endpoint_url": "https://minio.svc.local"},
            },
        },
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_projects_delete(mock_request, capsys):
    project_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
        call_command("croud", "projects", "delete", "--project-id", project_id)
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the project? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Project deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_projects_delete_flag(mock_request, capsys):
    project_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
        call_command("croud", "projects", "delete", "--project-id", project_id, "-y")
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/")
    mock_input.assert_not_called()

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Project deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_projects_delete_aborted(mock_request, capsys):
    project_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
        call_command("croud", "projects", "delete", "--project-id", project_id)
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the project? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Project deletion cancelled." in err_output


@mock.patch.object(
    Client,
    "request",
    return_value=(
        [
            {
                "id": "1",
                "name": "Test Project",
                "organization_id": "test.org.id",
                "region": "aks1.eastus.azure",
                "backup_location": {"location_type": "s3", "location": "some"},
            },
            {
                "id": "2",
                "name": "Test Project 2",
                "organization_id": "test.org.id",
                "region": "aks1.eastus.azure",
                "backup_location": None,
            },
        ],
        None,
    ),
)
def test_projects_list(mock_request):
    call_command("croud", "projects", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/projects/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_projects_list_with_organization_id(mock_request):
    org_id = gen_uuid()
    call_command("croud", "projects", "list", "--org-id", org_id)
    assert_rest(
        mock_request, RequestMethod.GET, f"/api/v2/organizations/{org_id}/projects/"
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_projects_get(mock_request):
    id = str(uuid.uuid4())
    call_command("croud", "projects", "get", id)
    assert_rest(mock_request, RequestMethod.GET, f"/api/v2/projects/{id}/")


@pytest.mark.parametrize(
    "added,message",
    [(True, "User added to project."), (False, "Role altered for user.")],
)
@mock.patch.object(Client, "request")
def test_projects_users_add(mock_request, added, message, capsys):
    mock_request.return_value = ({"added": added}, None)

    project_id = gen_uuid()

    # uid or email would be possible for the backend
    user = "test@crate.io"
    role_fqn = "project_admin"

    call_command(
        "croud",
        "projects",
        "users",
        "add",
        "--project-id",
        project_id,
        "--user",
        user,
        "--role",
        role_fqn,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/projects/{project_id}/users/",
        body={"user": user, "role_fqn": role_fqn},
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert message in err_output


@mock.patch.object(Client, "request", return_value=({}, None))
def test_projects_users_list(mock_request):
    project_id = gen_uuid()

    call_command("croud", "projects", "users", "list", "--project-id", project_id)
    assert_rest(
        mock_request, RequestMethod.GET, f"/api/v2/projects/{project_id}/users/"
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_projects_users_remove(mock_request):
    project_id = gen_uuid()

    # uid or email would be possible for the backend
    user = "test@crate.io"

    call_command(
        "croud",
        "projects",
        "users",
        "remove",
        "--project-id",
        project_id,
        "--user",
        user,
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/projects/{project_id}/users/{user}/",
    )


def test_role_fqn_transform():
    user = {
        "project_roles": [
            {"project_id": "project-1", "role_fqn": "project_admin"},
            {"project_id": "project-2", "role_fqn": "project_member"},
            {"project_id": "project-3", "role_fqn": "project_member"},
        ]
    }
    response = project_role_fqn_transform(user["project_roles"])
    assert response == "project_admin"


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_projects_edit(mock_request, capsys):
    project_id = gen_uuid()
    call_command("croud", "projects", "edit", "-p", project_id, "--name", "new-name")
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        f"/api/v2/projects/{project_id}/",
        body={"name": "new-name"},
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Project edited" in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_projects_edit_no_argument(mock_request, capsys):
    project_id = gen_uuid()
    with pytest.raises(SystemExit):
        call_command("croud", "projects", "edit", "-p", project_id)

    _, err_output = capsys.readouterr()
    assert "Error" in err_output
    assert "No input arguments found." in err_output
