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

pytestmark = pytest.mark.usefixtures("config")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_me(mock_request):
    call_command("croud", "me")
    assert_rest(mock_request, RequestMethod.GET, "/api/v2/users/me/")


@mock.patch.object(Client, "request", return_value=({}, None))
def test_me_edit_email(mock_request):
    call_command("croud", "me", "edit", "--email", "user@crate.io")
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        "/api/v2/users/me/",
        body={"email": "user@crate.io"},
    )
