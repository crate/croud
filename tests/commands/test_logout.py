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

from croud.logout import _logout_url
from tests.util import MockConfig, call_command


@mock.patch("croud.logout.print_info")
def test_logout(mock_print_info):
    conf = {
        "auth": {
            "current_context": "prod",
            "contexts": {"prod": {"token": "my-token"}},
        },
        "region": "bregenz.a1",
        "output_fmt": "table",
    }
    cfg = MockConfig(conf)

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
            call_command("croud", "logout", "--env", "prod")

    assert cfg.read_config()["auth"]["contexts"]["prod"]["token"] == ""
    mock_print_info.assert_called_once_with("You have been logged out.")


@pytest.mark.parametrize(
    "url,expected",
    [
        ("dev", "https://bregenz.a1.cratedb-dev.cloud/oauth2/logout"),
        ("prod", "https://bregenz.a1.cratedb.cloud/oauth2/logout"),
        ("PROD", "https://bregenz.a1.cratedb.cloud/oauth2/logout"),
        ("local", "http://localhost:8000/oauth2/logout"),
        ("invalid", "https://bregenz.a1.cratedb.cloud/oauth2/logout"),
    ],
)
def test_logout_urls(url, expected):
    assert _logout_url(url) == expected
