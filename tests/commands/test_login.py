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

from croud.config import Configuration
from croud.login import _login_url, get_org_id
from croud.server import Server
from tests.util import MockConfig, call_command


@mock.patch.object(Server, "stop")
@mock.patch.object(Server, "start")
@mock.patch("croud.login.asyncio.get_event_loop")
@mock.patch("croud.login.can_launch_browser", return_value=True)
@mock.patch("croud.login.open_page_in_browser")
@mock.patch("croud.login.print_info")
def test_login(
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
            with mock.patch("croud.login.get_org_id", return_value="my-org-id"):
                call_command("croud", "login", "--env", "dev")

    calls = [
        mock.call("A browser tab has been launched for you to login."),
        mock.call("Login successful."),
    ]
    mock_print_info.assert_has_calls(calls)
    config = cfg.read_config()
    assert config["auth"]["current_context"] == "dev"
    assert config["auth"]["contexts"]["dev"]["organization_id"] == "my-org-id"


@mock.patch.object(Server, "stop")
@mock.patch.object(Server, "start")
@mock.patch("croud.login.asyncio.get_event_loop")
@mock.patch("croud.login.can_launch_browser", return_value=True)
@mock.patch("croud.login.open_page_in_browser")
@mock.patch("croud.login.print_info")
def test_login_local(
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
            with mock.patch("croud.rest.Client.send", return_value=[None, None]):
                call_command("croud", "login", "--env", "local")

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
    mock_print_error, mock_can_launch_browser, mock_get_env
):
    with pytest.raises(SystemExit) as e_info:
        call_command("croud", "login")

    mock_print_error.assert_called_once_with(
        "Login only works with a valid browser installed."
    )
    assert e_info.value.code == 1


@pytest.mark.parametrize(
    "url,expected",
    [
        ("dev", "https://bregenz.a1.cratedb-dev.cloud/oauth2/login?cli=true"),
        ("prod", "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true"),
        ("PROD", "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true"),
        ("local", "http://localhost:8000/oauth2/login?cli=true"),
        ("invalid", "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true"),
    ],
)
def test_login_urls(url, expected):
    assert _login_url(url) == expected


@pytest.mark.parametrize("org_id_param", [None, "some-id"])
def test_get_org_id(org_id_param):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)
    cfg.conf["auth"]["contexts"]["dev"]["organization_id"]
    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
            with mock.patch(
                "croud.rest.Client.send",
                return_value=[{"organization_id": org_id_param}, None],
            ):
                org_id = get_org_id()
    assert org_id == org_id_param
