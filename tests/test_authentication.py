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

from argparse import Namespace
from unittest import mock

from croud.logout import _logout_url, logout
from tests.util import MockConfig


class TestLogout:
    @mock.patch("croud.logout.asyncio.get_event_loop")
    @mock.patch("croud.logout.print_info")
    def test_logout(self, mock_print_info, mock_loop):
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
                logout(Namespace(env="prod"))

        assert cfg.read_config()["auth"]["contexts"]["prod"]["token"] == ""
        mock_print_info.assert_called_once_with("You have been logged out.")

    def test_logout_urls_from_valid_envs(self):
        url = _logout_url("dev")
        assert "https://bregenz.a1.cratedb-dev.cloud/oauth2/logout" == url

        url = _logout_url("prod")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/logout" == url

        url = _logout_url("PROD")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/logout" == url

        url = _logout_url("local")
        assert "http://localhost:8000/oauth2/logout" == url

    def test_env_fallback_url(self):
        url = _logout_url("invalid")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/logout" == url
