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
from croud.users.commands import transform_roles_list
from tests.util import assert_rest, call_command, gen_uuid

pytestmark = pytest.mark.usefixtures("config")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_users_list(mock_request):
    call_command("croud", "users", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/users/", params=None)


@mock.patch.object(Client, "request", return_value=({}, None))
def test_users_list_no_org(mock_request, capsys):
    call_command("croud", "users", "list", "--no-org")
    assert_rest(
        mock_request, RequestMethod.GET, "/api/v2/users/", params={"no-roles": "1"}
    )
    _, err = capsys.readouterr()
    assert "The --no-org argument is deprecated. Please use --no-roles instead." in err


@mock.patch.object(Client, "request", return_value=({}, None))
def test_users_list_no_roles(mock_request):
    call_command("croud", "users", "list", "--no-roles")
    assert_rest(
        mock_request, RequestMethod.GET, "/api/v2/users/", params={"no-roles": "1"}
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_users_list_no_org_no_roles(mock_request, capsys):
    call_command("croud", "users", "list", "--no-roles", "--no-org")
    assert_rest(
        mock_request, RequestMethod.GET, "/api/v2/users/", params={"no-roles": "1"}
    )
    _, err = capsys.readouterr()
    assert "The --no-org argument is deprecated. Please use --no-roles instead." in err


@mock.patch.object(Client, "request", return_value=({}, None))
def test_users_roles_list(mock_request):
    call_command("croud", "users", "roles", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/roles/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_transform_roles_list(mock_request):
    user = {
        "organization_roles": [
            {"organization_id": "org-1", "role_fqn": "org_admin"},
            {"organization_id": "org-2", "role_fqn": "org_member"},
            {"organization_id": "org-3", "role_fqn": "org_member"},
        ],
        "project_roles": [
            {"project_id": "project-1", "role_fqn": "project_admin"},
            {"project_id": "project-2", "role_fqn": "project_member"},
            {"project_id": "project-3", "role_fqn": "project_member"},
        ],
    }
    response = transform_roles_list("organization_id")(user["organization_roles"])
    assert response == "org-1: org_admin,\norg-2: org_member,\norg-3: org_member"
    response = transform_roles_list("project_id")(user["project_roles"])
    assert response == (
        "project-1: project_admin,\n"
        "project-2: project_member,\n"
        "project-3: project_member"
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_users_delete(mock_request, capsys):
    user_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Y"]) as mock_input:
        call_command("croud", "users", "delete", "--user-id", user_id)
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/users/{user_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the user? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "User deleted." in err_output
