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

from croud.config import Configuration
from croud.organizations.users.commands import (
    role_fqn_transform as organization_role_fqn_transform,
)
from croud.rest import Client
from croud.session import RequestMethod
from tests.util import assert_rest, call_command


def gen_uuid() -> str:
    return str(uuid.uuid4())


config_org_id = gen_uuid()
FALLBACK_ORG_ID_CONFIG: dict = {
    "auth": {
        "current_context": "prod",
        "contexts": {
            "prod": {"token": "", "organization_id": config_org_id},
            "dev": {"token": "", "organization_id": config_org_id},
            "local": {"token": "", "organization_id": config_org_id},
        },
    },
    "region": "bregenz.a1",
    "output_fmt": "table",
}


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_create(mock_send, mock_load_config):
    call_command("croud", "organizations", "create", "--name", "test-org")
    assert_rest(
        mock_send,
        RequestMethod.POST,
        "/api/v2/organizations/",
        body={"name": "test-org"},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_create_name_plan_type(mock_send, mock_load_config):
    call_command(
        "croud", "organizations", "create", "--name", "test-org", "--plan-type", "3"
    )
    assert_rest(
        mock_send,
        RequestMethod.POST,
        "/api/v2/organizations/",
        body={"name": "test-org", "plan_type": 3},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_edit_name(mock_send, mock_load_config):
    org_id = gen_uuid()
    call_command(
        "croud", "organizations", "edit", "--name", "new-org-name", "--org-id", org_id
    )
    assert_rest(
        mock_send,
        RequestMethod.PUT,
        f"/api/v2/organizations/{org_id}/",
        body={"name": "new-org-name"},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_edit_plan_type(mock_send, mock_load_config):
    org_id = gen_uuid()
    call_command(
        "croud", "organizations", "edit", "--plan-type", "3", "--org-id", org_id
    )
    assert_rest(
        mock_send,
        RequestMethod.PUT,
        f"/api/v2/organizations/{org_id}/",
        body={"plan_type": 3},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_edit_name_plan_type(mock_send, mock_load_config):
    org_id = gen_uuid()
    call_command(
        "croud",
        "organizations",
        "edit",
        "--name",
        "new-org-name",
        "--plan-type",
        "3",
        "--org-id",
        org_id,
    )
    assert_rest(
        mock_send,
        RequestMethod.PUT,
        f"/api/v2/organizations/{org_id}/",
        body={"name": "new-org-name", "plan_type": 3},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_edit_no_arguments(mock_send, mock_load_config, capsys):
    org_id = gen_uuid()
    with pytest.raises(SystemExit):
        call_command("croud", "organizations", "edit", "--org-id", org_id)

    _, err = capsys.readouterr()
    assert "No input arguments found." in err


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_list(mock_send, mock_load_config):
    call_command("croud", "organizations", "list")
    assert_rest(mock_send, RequestMethod.GET, "/api/v2/organizations/")


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_delete(mock_send, mock_load_config, capsys):
    org_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Y"]) as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id)
    assert_rest(mock_send, RequestMethod.DELETE, f"/api/v2/organizations/{org_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the organization? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Organization deleted." in err_output


@mock.patch("croud.config.Configuration.set_organization_id")
@mock.patch("croud.config.load_config", return_value=FALLBACK_ORG_ID_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {"errors": "Message"}))
def test_delete_failure_org_id_not_deleted_from_config(
    mock_send, mock_load_config, mock_set_config, capsys
):
    with mock.patch("builtins.input", side_effect=["Y"]):
        call_command("croud", "organizations", "delete")
    assert_rest(
        mock_send,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{mock_load_config.return_value['auth']['contexts']['local']['organization_id']}/",  # noqa
    )
    _, err = capsys.readouterr()
    assert err is not None
    assert (
        mock_set_config.called is False
    )  # This means that the org_id is still in the local config


@mock.patch("croud.config.Configuration.set_organization_id")
@mock.patch("croud.config.load_config", return_value=FALLBACK_ORG_ID_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_delete_org_id_from_local_config(
    mock_send, mock_load_config, mock_set_config, capsys
):
    with mock.patch("builtins.input", side_effect=["Y"]):
        call_command("croud", "organizations", "delete")
    assert_rest(
        mock_send,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{mock_load_config.return_value['auth']['contexts']['local']['organization_id']}/",  # noqa
    )
    _, err = capsys.readouterr()
    assert (
        mock_set_config.called is True
    )  # This means that the org_id was deleted from the local config


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_delete_flag(mock_send, mock_load_config, capsys):
    org_id = gen_uuid()
    with mock.patch("builtins.input") as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id, "-y")
    assert_rest(mock_send, RequestMethod.DELETE, f"/api/v2/organizations/{org_id}/")
    mock_input.assert_not_called()

    _, err_output = capsys.readouterr()
    assert "Organization deleted." in err_output


@pytest.mark.parametrize("input", ["", "N", "No", "cancel"])
@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_delete_aborted(mock_send, mock_load_config, capsys, input):
    org_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=[input]) as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id)
    mock_send.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the organization? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Organization deletion cancelled." in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=(None, {}))
def test_delete_aborted_with_input(mock_send, mock_load_config, capsys):
    org_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["N"]) as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id)
    mock_send.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the organization? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Organization deletion cancelled." in err_output


@pytest.mark.parametrize(
    "added,message",
    [(True, "User added to organization."), (False, "Role altered for user.")],
)
@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({"added": True}, None))
def test_users_add(mock_send, mock_load_config, added, message, capsys):
    mock_send.return_value = ({"added": added}, None)

    org_id = gen_uuid()
    user = "test@crate.io"
    role_fqn = "org_admin"

    call_command(
        "croud",
        "organizations",
        "users",
        "add",
        "--user",
        user,
        "--org-id",
        org_id,
        "--role",
        role_fqn,
    )
    assert_rest(
        mock_send,
        RequestMethod.POST,
        f"/api/v2/organizations/{org_id}/users/",
        body={"user": user, "role_fqn": role_fqn},
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert message in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_users_list(mock_send, mock_load_config):
    org_id = gen_uuid()

    call_command("croud", "organizations", "users", "list", "--org-id", org_id)
    assert_rest(mock_send, RequestMethod.GET, f"/api/v2/organizations/{org_id}/users/")


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_users_remove(mock_send, mock_load_config):
    org_id = gen_uuid()
    user = "test@crate.io"

    call_command(
        "croud", "organizations", "users", "remove", "--user", user, "--org-id", org_id
    )
    assert_rest(
        mock_send, RequestMethod.DELETE, f"/api/v2/organizations/{org_id}/users/{user}/"
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
def test_role_fqn_transform(mock_load_config):
    user = {
        "organization_roles": [
            {"organization_id": "org-1", "role_fqn": "organization_admin"},
            {"organization_id": "org-2", "role_fqn": "organization_member"},
            {"organization_id": "org-3", "role_fqn": "organization_member"},
        ]
    }
    response = organization_role_fqn_transform(user["organization_roles"])
    assert response == "organization_admin"