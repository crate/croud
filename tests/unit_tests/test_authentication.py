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

import copy
from argparse import Namespace
from typing import Dict
from unittest import mock

import pytest

from croud.config import Configuration
from croud.login import _login_url, login
from croud.logout import _logout_url, logout
from croud.server import Server


class MockConfig:
    """
    A mocked configuration which emulates reading and writing file from/to disk.
    """

    def __init__(self, config: Dict) -> None:
        self.conf = copy.deepcopy(config)

    def read_config(self) -> Dict:
        return self.conf

    def write_config(self, config) -> None:
        self.conf = config


class TestLogin:
    @mock.patch.object(Server, "stop")
    @mock.patch.object(Server, "start")
    @mock.patch("croud.login.asyncio.get_event_loop")
    @mock.patch("croud.login.can_launch_browser", return_value=True)
    @mock.patch("croud.login.open_page_in_browser")
    @mock.patch("croud.login.print_info")
    def test_login_success(
        self,
        mock_print_info,
        mock_open_page_in_browser,
        mock_can_launch_browser,
        mock_loop,
        mock_start,
        mock_stop,
    ):
        cfg = MockConfig(Configuration.DEFAULT_CONFIG)

        with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
            with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
                login(Namespace(env="dev"))

        calls = [
            mock.call("A browser tab has been launched for you to login."),
            mock.call("Login successful."),
        ]
        mock_print_info.assert_has_calls(calls)
        assert cfg.read_config()["auth"]["current_context"] == "dev"

    @mock.patch.object(Server, "stop")
    @mock.patch.object(Server, "start")
    @mock.patch("croud.login.asyncio.get_event_loop")
    @mock.patch("croud.login.can_launch_browser", return_value=True)
    @mock.patch("croud.login.open_page_in_browser")
    @mock.patch("croud.login.print_info")
    def test_local_login(
        self,
        mock_print_info,
        mock_open_page_in_browser,
        mock_can_launch_browser,
        mock_loop,
        mock_start,
        mock_stop,
    ):
        """
        Test for a bug that caused that upon login to local env the local token
        was overwritten by the dev token.
        """
        conf = {
            "auth": {
                "current_context": "prod",
                "contexts": {
                    "prod": {"token": "prod-token"},
                    "dev": {"token": "dev-token"},
                    "local": {"token": ""},
                },
            },
            "region": "bregenz.a1",
            "output_fmt": "table",
        }
        cfg = MockConfig(conf)

        with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
            with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
                login(Namespace(env="local"))

        new_cfg = cfg.read_config()
        assert new_cfg["auth"]["current_context"] == "local"
        assert (
            new_cfg["auth"]["contexts"]["local"]["token"]
            != new_cfg["auth"]["contexts"]["dev"]["token"]
        )
        assert (
            new_cfg["auth"]["contexts"]["local"]["token"]
            != new_cfg["auth"]["contexts"]["prod"]["token"]
        )

    @mock.patch("croud.config.Configuration.get_env", return_value="dev")
    @mock.patch("croud.login.can_launch_browser", return_value=False)
    @mock.patch("croud.login.print_error")
    def test_login_no_valid_browser(
        self, mock_print_error, mock_can_launch_browser, mock_get_env
    ):
        with pytest.raises(SystemExit) as e_info:
            login(Namespace(env=None))

        mock_print_error.assert_called_once_with(
            "Login only works with a valid browser installed."
        )
        assert e_info.value.code == 1

    def test_login_urls_from_valid_envs(self):
        url = _login_url("dev")
        assert "https://bregenz.a1.cratedb-dev.cloud/oauth2/login?cli=true" == url

        url = _login_url("prod")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true" == url

        url = _login_url("PROD")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true" == url

        url = _login_url("local")
        assert "http://localhost:8000/oauth2/login?cli=true" == url

    def test_env_fallback_url(self):
        url = _login_url("invalid")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true" == url


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
