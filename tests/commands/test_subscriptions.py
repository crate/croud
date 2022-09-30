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
