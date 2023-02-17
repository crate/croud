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

from croud.api import Client, RequestMethod
from tests.util import assert_rest, call_command, gen_uuid


@mock.patch.object(Client, "request", return_value=({}, None))
def test_subscriptions_list(mock_request):
    call_command("croud", "subscriptions", "list")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/subscriptions/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_subscriptions_list_with_organization_id(mock_request):
    org_id = gen_uuid()
    call_command("croud", "subscriptions", "list", "--org-id", org_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/organizations/{org_id}/subscriptions/",
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_subscriptions_get(mock_request):
    id = str(uuid.uuid4())
    call_command("croud", "subscriptions", "get", id)
    assert_rest(mock_request, RequestMethod.GET, f"/api/v2/subscriptions/{id}/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_subscriptions_create(mock_request):
    call_command(
        "croud",
        "subscriptions",
        "create",
        "--type",
        "contract",
        "--org-id",
        "organization-id",
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/subscriptions/",
        body={"type": "contract", "organization_id": "organization-id"},
    )


@mock.patch.object(
    Client,
    "request",
    return_value=(
        {
            "id": "123",
            "name": "test",
            "organization_id": "test",
            "state": "TERMINATING",
            "provider": "stripe",
        },
        None,
    ),
)
def test_subscriptions_delete(mock_request, capsys):
    sub_id = gen_uuid()
    with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
        call_command("croud", "subscriptions", "delete", "--subscription-id", sub_id)
    assert_rest(mock_request, RequestMethod.DELETE, f"/api/v2/subscriptions/{sub_id}/")
    mock_input.assert_called_once_with(
        "Are you sure you want to cancel this subscription? "
        "This will delete any clusters running in this subscription. [yN] "
    )

    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Subscription cancelled." in err_output
