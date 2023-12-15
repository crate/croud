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
from datetime import datetime, timedelta
from unittest import mock

import pytest

from croud.api import Client, RequestMethod
from croud.organizations.users.commands import (
    role_fqn_transform as organization_role_fqn_transform,
)
from tests.util import assert_rest, call_command, gen_uuid

pytestmark = pytest.mark.usefixtures("config")

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


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_create(mock_request):
    call_command("croud", "organizations", "create", "--name", "test-org")
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/",
        body={"name": "test-org"},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_create_plan_type(mock_request):
    call_command(
        "croud", "organizations", "create", "--name", "test-org", "--plan-type", "3"
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/organizations/",
        body={"name": "test-org", "plan_type": 3},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_edit(mock_request):
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
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/organizations/{org_id}/",
        body={"name": "new-org-name", "plan_type": 3},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_edit_name(mock_request):
    org_id = gen_uuid()
    call_command(
        "croud", "organizations", "edit", "--name", "new-org-name", "--org-id", org_id
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/organizations/{org_id}/",
        body={"name": "new-org-name"},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_edit_plan_type(mock_request):
    org_id = gen_uuid()
    call_command(
        "croud", "organizations", "edit", "--plan-type", "3", "--org-id", org_id
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/v2/organizations/{org_id}/",
        body={"plan_type": 3},
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_organizations_edit_no_arguments(mock_request, capsys):
    org_id = gen_uuid()
    with pytest.raises(SystemExit):
        call_command("croud", "organizations", "edit", "--org-id", org_id)

    _, err = capsys.readouterr()
    assert "No input arguments found." in err


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_list(mock_request):
    call_command("croud", "organizations", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/organizations/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_get(mock_request):
    id = str(uuid.uuid4())
    call_command("croud", "organizations", "get", id)
    assert_rest(mock_request, RequestMethod.GET, f"/api/v2/organizations/{id}/")


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_organizations_delete(mock_request, capsys):
    org_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["Y"]) as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id)
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/organizations/{org_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the organization? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Organization deleted." in err_output


@mock.patch.object(Client, "request", return_value=(None, {"errors": "Message"}))
def test_organizations_delete_failure_org_id_not_deleted_from_config(
    mock_request, capsys, config
):
    org_id = gen_uuid()
    config.set_organization_id(config.name, org_id)

    with mock.patch("builtins.input", side_effect=["Y"]):
        call_command("croud", "organizations", "delete")

    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{org_id}/",
    )

    _, err = capsys.readouterr()
    assert err is not None
    assert config.organization == org_id


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_delete_org_id_from_local_config(
    mock_request,
    capsys,
    config,
):
    org_id = gen_uuid()
    config.set_organization_id(config.name, org_id)

    with mock.patch("builtins.input", side_effect=["Y"]):
        call_command("croud", "organizations", "delete")

    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{org_id}/",
    )

    assert config.organization is None


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_organizations_delete_flag(mock_request, capsys):
    org_id = gen_uuid()
    with mock.patch("builtins.input") as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id, "-y")
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/organizations/{org_id}/")
    mock_input.assert_not_called()

    _, err_output = capsys.readouterr()
    assert "Organization deleted." in err_output


@pytest.mark.parametrize("input", ["", "N", "No", "cancel"])
@mock.patch.object(Client, "request", return_value=(None, {}))
def test_organizations_delete_aborted(mock_request, capsys, input):
    org_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=[input]) as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id)
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the organization? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Organization deletion cancelled." in err_output


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_organizations_delete_aborted_with_input(mock_request, capsys):
    org_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["N"]) as mock_input:
        call_command("croud", "organizations", "delete", "--org-id", org_id)
    mock_request.assert_not_called()
    mock_input.assert_called_once_with(
        "Are you sure you want to delete the organization? [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Organization deletion cancelled." in err_output


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_auditlogs_list(mock_request):
    org_id = gen_uuid()

    call_command("croud", "organizations", "auditlogs", "list", "--org-id", org_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/auditlogs/",
        params={},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_auditlogs_list_filtered(mock_request):
    org_id = gen_uuid()

    call_command(
        "croud",
        "organizations",
        "auditlogs",
        "list",
        "--org-id",
        org_id,
        "--action",
        "organization.create",
        "--from",
        "2019-10-11T12:13:14",
        "--to",
        "2019-11-12T12:34:56",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/auditlogs/",
        params={
            "action": "organization.create",
            "from": "2019-10-11T12:13:14",
            "to": "2019-11-12T12:34:56",
        },
    )


@mock.patch.object(Client, "request", side_effect=[([{"id": 123}], None), ([], None)])
def test_organizations_auditlogs_list_pagination(mock_request: mock.Mock):
    org_id = gen_uuid()

    call_command("croud", "organizations", "auditlogs", "list", "--org-id", org_id)

    mock_request.call_args_list[0].assert_called_with(
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/auditlogs/",
        params={},
    )
    mock_request.call_args_list[1].assert_called_with(
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/auditlogs/",
        params={"last": 123},
    )


@pytest.mark.parametrize(
    "added,message",
    [(True, "User added to organization."), (False, "Role altered for user.")],
)
@mock.patch.object(Client, "request")
def test_organizations_users_add(mock_request, added, message, capsys):
    mock_request.return_value = ({"added": added}, None)

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
        mock_request,
        RequestMethod.POST,
        f"/api/v2/organizations/{org_id}/users/",
        body={"user": user, "role_fqn": role_fqn},
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert message in err_output


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_users_list(mock_request):
    org_id = gen_uuid()

    call_command("croud", "organizations", "users", "list", "--org-id", org_id)
    assert_rest(
        mock_request, RequestMethod.GET, f"/api/v2/organizations/{org_id}/users/"
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_users_remove(mock_request):
    org_id = gen_uuid()
    user = "test@crate.io"

    call_command(
        "croud", "organizations", "users", "remove", "--user", user, "--org-id", org_id
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{org_id}/users/{user}/",
    )


def test_role_fqn_transform():
    user = {
        "organization_roles": [
            {"organization_id": "org-1", "role_fqn": "organization_admin"},
            {"organization_id": "org-2", "role_fqn": "organization_member"},
            {"organization_id": "org-3", "role_fqn": "organization_member"},
        ]
    }
    response = organization_role_fqn_transform(user["organization_roles"])
    assert response == "organization_admin"


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_files_get(mock_request):
    org_id = gen_uuid()
    file_id = gen_uuid()
    call_command(
        "croud",
        "organizations",
        "files",
        "get",
        "--org-id",
        org_id,
        "--file-id",
        file_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/files/{file_id}/",
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_files_list(mock_request):
    org_id = gen_uuid()

    call_command("croud", "organizations", "files", "list", "--org-id", org_id)
    assert_rest(
        mock_request, RequestMethod.GET, f"/api/v2/organizations/{org_id}/files/"
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_files_delete(mock_request):
    org_id = gen_uuid()
    file_id = gen_uuid()

    call_command(
        "croud",
        "organizations",
        "files",
        "delete",
        "--org-id",
        org_id,
        "--file-id",
        file_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{org_id}/files/{file_id}/",
    )


@mock.patch("croud.organizations.commands.os.path.isfile", return_value=True)
@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_files_create(mock_request, mock_isfile):
    org_id = gen_uuid()
    file_path = "/path/to/file.json.gz"
    file_name = "my-file"
    call_command(
        "croud",
        "organizations",
        "files",
        "create",
        "--org-id",
        org_id,
        "--file-path",
        file_path,
        "--name",
        file_name,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/organizations/{org_id}/files/",
        body={"name": file_name},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_secrets_list(mock_request):
    org_id = gen_uuid()

    call_command("croud", "organizations", "secrets", "list", "--org-id", org_id)
    assert_rest(
        mock_request, RequestMethod.GET, f"/api/v2/organizations/{org_id}/secrets/"
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_secrets_aws_create(mock_request):
    org_id = gen_uuid()
    name = "my_secret"
    secret_type = "AWS"
    access_key = "my_access_key"
    secret_key = "my_secret_key"

    call_command(
        "croud",
        "organizations",
        "secrets",
        "create",
        "--org-id",
        org_id,
        "--name",
        name,
        "--type",
        secret_type,
        "--access-key",
        access_key,
        "--secret-key",
        secret_key,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/organizations/{org_id}/secrets/",
        body={
            "name": name,
            "type": secret_type,
            "data": {"access_key": access_key, "secret_key": secret_key},
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_secrets_azure_create(mock_request):
    org_id = gen_uuid()
    name = "my_secret"
    secret_type = "AZURE"
    connection_string = "https://my-storage-account.blob.core.windows.net/my-container?my-auth-params"  # noqa

    call_command(
        "croud",
        "organizations",
        "secrets",
        "create",
        "--org-id",
        org_id,
        "--name",
        name,
        "--type",
        secret_type,
        "--connection-string",
        connection_string,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/organizations/{org_id}/secrets/",
        body={
            "name": name,
            "type": secret_type,
            "data": {
                "azure_secret": {"connection_string": connection_string},
            },
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_secrets_delete(mock_request):
    org_id = gen_uuid()

    call_command(
        "croud",
        "organizations",
        "secrets",
        "delete",
        "--org-id",
        org_id,
        "--secret-id",
        "my_secret_id",
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{org_id}/secrets/my_secret_id/",
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_list(mock_request):
    org_id = gen_uuid()

    call_command("croud", "organizations", "credits", "list", "--org-id", org_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/credits/",
        params={},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_list_filter_status(mock_request):
    org_id = gen_uuid()

    call_command(
        "croud",
        "organizations",
        "credits",
        "list",
        "--org-id",
        org_id,
        "--status",
        "ACTIVE,EXPIRED",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/credits/",
        params={"status": "ACTIVE,EXPIRED"},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_create(mock_request):
    org_id = gen_uuid()
    amount = 123.45
    expiration_date = datetime.utcnow() + timedelta(days=30)
    comment = "Free Trial"

    call_command(
        "croud",
        "organizations",
        "credits",
        "create",
        "--org-id",
        org_id,
        "--amount",
        str(amount),
        "--expiration-date",
        expiration_date.isoformat(),
        "--comment",
        comment,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/organizations/{org_id}/credits/",
        body={
            "amount": amount * 100,
            "expiration_date": expiration_date.isoformat(),
            "comment": comment,
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_expire(mock_request):
    org_id = gen_uuid()

    call_command(
        "croud",
        "organizations",
        "credits",
        "expire",
        "--org-id",
        org_id,
        "--credit-id",
        "my_credit_id",
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/organizations/{org_id}/credits/my_credit_id/",
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_edit(mock_request):
    org_id = gen_uuid()
    expiration_date = datetime.utcnow() + timedelta(days=60)
    call_command(
        "croud",
        "organizations",
        "credits",
        "edit",
        "--org-id",
        org_id,
        "--credit-id",
        "my_credit_id",
        "--amount",
        str(234.56),
        "--expiration-date",
        expiration_date.isoformat(),
        "--comment",
        "Starter Package",
    )
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        f"/api/v2/organizations/{org_id}/credits/my_credit_id/",
        body={
            "amount": 23456,
            "expiration_date": expiration_date.isoformat(),
            "comment": "Starter Package",
        },
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_edit_amount(mock_request):
    org_id = gen_uuid()
    call_command(
        "croud",
        "organizations",
        "credits",
        "edit",
        "--org-id",
        org_id,
        "--credit-id",
        "my_credit_id",
        "--amount",
        str(234.56),
    )
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        f"/api/v2/organizations/{org_id}/credits/my_credit_id/",
        body={"amount": 23456},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_organizations_credits_edit_expiration_date(mock_request):
    org_id = gen_uuid()
    expiration_date = datetime.utcnow() + timedelta(days=60)
    call_command(
        "croud",
        "organizations",
        "credits",
        "edit",
        "--org-id",
        org_id,
        "--credit-id",
        "my_credit_id",
        "--expiration-date",
        expiration_date.isoformat(),
    )
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        f"/api/v2/organizations/{org_id}/credits/my_credit_id/",
        body={"expiration_date": expiration_date.isoformat()},
    )


@mock.patch.object(Client, "request", return_value=(None, {}))
def test_organizations_credits_edit_no_arguments(mock_request, capsys):
    org_id = gen_uuid()
    with pytest.raises(SystemExit):
        call_command(
            "croud",
            "organizations",
            "credits",
            "edit",
            "--org-id",
            org_id,
            "--credit-id",
            "my_credit_id",
        )

    _, err = capsys.readouterr()
    assert "No input arguments found." in err
