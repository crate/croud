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

from http.cookies import Morsel
from unittest import mock

import pytest

from croud.config import Configuration
from croud.session import HttpSession, RequestMethod, cloud_url


@pytest.mark.asyncio
async def test_request_unauthorized(fake_cloud_connector):
    with pytest.raises(SystemExit) as cm:
        async with HttpSession(
            "dev", "", url="https://cratedb.local", conn=fake_cloud_connector
        ) as session:
            with mock.patch("croud.session.print_error") as mock_print_error:
                await session.fetch(RequestMethod.GET, "/data/data-key")

    assert cm.value.code == 1
    mock_print_error.assert_called_once_with(
        "Unauthorized. Use `croud login` to login to CrateDB Cloud."
    )


@mock.patch.object(Configuration, "get_env", return_value="dev")
def test_correct_url(mock_env):
    region = "bregenz.a1"

    url = cloud_url("prod", region)
    assert url == f"https://{region}.cratedb.cloud"

    url = cloud_url("dev", region)
    assert url == f"https://{region}.cratedb-dev.cloud"

    url = cloud_url("local", region)
    assert url == "http://localhost:8000"

    region = "westeurope.azure"
    url = cloud_url("prod", region)
    assert url == f"https://{region}.cratedb.cloud"


@pytest.mark.asyncio
async def test_on_new_token():
    update_config = mock.Mock()
    async with HttpSession(
        "dev", "old_token", "eastus.azure", on_new_token=update_config
    ) as session:
        session_cookie = Morsel()
        session_cookie.set("session", "new_token", None)
        session.client.cookie_jar.update_cookies({"session": session_cookie})

    update_config.assert_called_once_with("new_token")
