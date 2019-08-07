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

from croud.config import Configuration
from croud.projects.users.commands import (
    role_fqn_transform as project_role_fqn_transform,
)
from croud.rest import Client
from croud.session import RequestMethod
from tests.util import assert_rest, call_command, gen_uuid


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_projects_create(mock_send, mock_load_config):
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
        mock_send,
        RequestMethod.POST,
        "/api/v2/projects/",
        body={"name": "new-project", "organization_id": "organization-id"},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_projects_delete(mock_send, mock_load_config, capsys):
    project_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
        call_command("croud", "projects", "delete", "--project-id", project_id)
    assert_rest(mock_send, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the project? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Project deleted." in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_projects_delete_flag(mock_send, mock_load_config, capsys):
    project_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
        call_command("croud", "projects", "delete", "--project-id", project_id, "-y")
    assert_rest(mock_send, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/")
    mock_input.assert_not_called()

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Project deleted." in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_projects_delete_aborted(mock_send, mock_load_config, capsys):
    project_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
        call_command("croud", "projects", "delete", "--project-id", project_id)
    mock_send.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the project? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Project deletion cancelled." in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_projects_list(mock_send, mock_load_config):
    call_command("croud", "projects", "list")
    assert_rest(mock_send, RequestMethod.GET, "/api/v2/projects/")


@pytest.mark.parametrize(
    "added,message",
    [(True, "User added to project."), (False, "Role altered for user.")],
)
@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send")
def test_projects_users_add(mock_send, mock_load_config, added, message, capsys):
    mock_send.return_value = ({"added": added}, None)

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
        mock_send,
        RequestMethod.POST,
        f"/api/v2/projects/{project_id}/users/",
        body={"user": user, "role_fqn": role_fqn},
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert message in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_projects_users_list(mock_send, mock_load_config):
    project_id = gen_uuid()

    call_command("croud", "projects", "users", "list", "--project-id", project_id)
    assert_rest(mock_send, RequestMethod.GET, f"/api/v2/projects/{project_id}/users/")


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_projects_users_remove(mock_send, mock_load_config):
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
        mock_send, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/users/{user}/"
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
def test_role_fqn_transform(mock_load_config):
    user = {
        "project_roles": [
            {"project_id": "project-1", "role_fqn": "project_admin"},
            {"project_id": "project-2", "role_fqn": "project_member"},
            {"project_id": "project-3", "role_fqn": "project_member"},
        ]
    }
    response = project_role_fqn_transform(user["project_roles"])
    assert response == "project_admin"
