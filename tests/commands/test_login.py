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

from croud.config import CONFIG
from croud.login import get_org_id, login_path
from croud.server import Server
from tests.util import call_command


@mock.patch.object(Server, "wait_for_shutdown")
@mock.patch.object(Server, "start_in_background")
@mock.patch("croud.login.can_launch_browser", return_value=True)
@mock.patch("croud.login.open_page_in_browser")
@mock.patch("croud.login.print_info")
def test_login(
    mock_print_info,
    mock_open_page_in_browser,
    mock_can_launch_browser,
    mock_start_in_background,
    mock_wait_for_shutdown,
    config,
):
    with mock.patch("croud.login.get_org_id", return_value="my-org-id"):
        call_command("croud", "login", "--idp", "cognito")

    calls = [
        mock.call("A browser tab has been launched for you to login."),
        mock.call("Login successful."),
    ]
    mock_print_info.assert_has_calls(calls)
    assert config.profile["organization-id"] == "my-org-id"


@mock.patch("croud.login.can_launch_browser", return_value=False)
@mock.patch("croud.login.print_error")
def test_login_no_valid_browser(mock_print_error, mock_can_launch_browser, config):
    with pytest.raises(SystemExit) as e_info:
        call_command("croud", "login", "--idp", "cognito")

    mock_print_error.assert_called_once_with(
        "Login only works with a valid browser installed."
    )
    assert e_info.value.code == 1


@mock.patch("croud.login.can_launch_browser", return_value=True)
@mock.patch("croud.login.print_error")
def test_login_no_idp(_mock_print_error, _mock_can_launch_browser, config, capsys):
    with pytest.raises(SystemExit) as e_info:
        call_command("croud", "login")

    assert e_info.value.code == 2
    _, err_output = capsys.readouterr()
    assert "The following arguments are required: --idp" in err_output


@pytest.mark.parametrize("org_id_param", [None, "some-id"])
def test_get_org_id(org_id_param, config):
    with mock.patch(
        "croud.api.Client.request",
        return_value=[{"organization_id": org_id_param}, None],
    ):
        org_id = get_org_id()
    assert org_id == org_id_param


@pytest.mark.parametrize(
    "idp,expected",
    [(None, "/oauth2/login?cli=true"), ("idp", "/oauth2/idp/login?cli=true")],
)
def test_login_path(idp, expected):
    assert login_path(idp) == expected


@pytest.mark.parametrize(
    "idp,expected",
    [
        ("azuread", "/oauth2/azuread/login?cli=true"),
        ("cognito", "/oauth2/cognito/login?cli=true"),
        ("github", "/oauth2/github/login?cli=true"),
        ("google", "/oauth2/google/login?cli=true"),
        ("twitter", None),
    ],
)
@mock.patch("croud.login.get_org_id", return_value="my-org-id")
@mock.patch("croud.login.print_info")
@mock.patch.object(Server, "wait_for_shutdown")
@mock.patch.object(Server, "start_in_background")
@mock.patch("croud.login.can_launch_browser", return_value=True)
def test_login_idp(
    _mock_can_launch_browser,
    _mock_start_in_background,
    _mock_wait_for_shutdown,
    _mock_print_info,
    _mock_get_org_id,
    idp,
    expected,
):
    with mock.patch("croud.login.open_page_in_browser") as open_page:
        if expected:
            call_command("croud", "login", "--idp", idp)
            open_page.assert_called_once_with(CONFIG.endpoint + expected)
        else:
            with pytest.raises(SystemExit) as e_info:
                call_command("croud", "login", "--idp", idp)
                open_page.assert_not_called()
                assert e_info.value.code == 1
