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
from unittest import mock

import pytest

from croud.config import Configuration
from croud.util import (
    can_launch_browser,
    confirm_prompt,
    get_platform_info,
    is_wsl,
    open_page_in_browser,
    org_id_config_fallback,
    require_confirmation,
)


# This function was copied from the <https://github.com/Azure/azure-cli>
# project. See `LICENSE` for more information.
@mock.patch("webbrowser.open", autospec=True)
@mock.patch("subprocess.call", autospec=True)
def test_open_page_in_browser(subprocess_call_mock, webbrowser_open_mock):
    platform_name, release = get_platform_info()
    open_page_in_browser("http://foo")
    if is_wsl(platform_name, release):
        subprocess_call_mock.assert_called_once_with(
            ["cmd.exe", "/c", "start http://foo"]
        )
    else:
        webbrowser_open_mock.assert_called_once_with("http://foo", 2)


# This function was copied from the <https://github.com/Azure/azure-cli>
# project. See `LICENSE` for more information.
@mock.patch("croud.util.get_platform_info", autospec=True)
@mock.patch("webbrowser.get", autospec=True)
def test_can_launch_browser(webbrowser_get_mock, get_platform_mock):
    # WSL is always fine
    get_platform_mock.return_value = ("linux", "4.4.0-17134-microsoft")
    result = can_launch_browser()
    assert result

    # windows is always fine
    get_platform_mock.return_value = ("windows", "10")
    result = can_launch_browser()
    assert result

    # osx is always fine
    get_platform_mock.return_value = ("darwin", "10")
    result = can_launch_browser()
    assert result

    # now tests linux
    with mock.patch("os.environ", autospec=True) as env_mock:
        # when no GUI, return false
        get_platform_mock.return_value = ("linux", "4.15.0-1014-azure")
        env_mock.get.return_value = None
        result = can_launch_browser()
        assert not result

        # when there is gui, and browser is a good one, return True
        browser_mock = mock.MagicMock()
        browser_mock.name = "goodone"
        env_mock.get.return_value = "foo"
        result = can_launch_browser()
        assert result

        # when there is gui, but the browser is text mode, return False
        browser_mock = mock.MagicMock()
        browser_mock.name = "www-browser"
        webbrowser_get_mock.return_value = browser_mock
        env_mock.get.return_value = "foo"
        result = can_launch_browser()
        assert not result


@pytest.mark.parametrize(
    "msg,response,is_confirmed",
    [
        ("test", "y", True),
        ("Other thingy", "Yes", True),
        ("But not common phrases", "Yay", False),
        ("Nope Nope Nope", "huh?", False),
        ("Srsly?", "!", False),
    ],
)
def test_confirm_prompt(msg, response, is_confirmed):
    with mock.patch("builtins.input", side_effect=[response]) as mock_input:
        assert confirm_prompt(msg) is is_confirmed
        mock_input.assert_called_once_with(f"{msg} [yN] ")


@pytest.mark.parametrize(
    "confirm_msg,cancel_msg,args_yes_value,response,output",
    [
        ("Are you sure?", None, True, "y", "Command output"),
        ("Are you sure?", None, False, "y", "Command output"),
        ("Are you sure?", "Cancelled!", False, "n", "Cancelled!"),
    ],
)
def test_require_confirmation(
    confirm_msg, cancel_msg, args_yes_value, response, output, capsys
):
    kwargs = {}
    if cancel_msg is not None:
        kwargs["cancel_msg"] = cancel_msg

    @require_confirmation(confirm_msg=confirm_msg, **kwargs)
    def command(args: Namespace):
        print("Command output")

    args = Namespace(yes=args_yes_value)
    with mock.patch("builtins.input", side_effect=[response]) as mock_input:
        command(args)
        if args_yes_value:
            mock_input.assert_not_called()
        else:
            mock_input.assert_called()

    out, err_output = capsys.readouterr()
    if err_output != "":
        assert out in err_output
    else:
        assert output in out


@pytest.mark.parametrize(
    "current_context,prod_org_id,dev_org_id,org_id_arg,env_arg,expected",
    [
        ("dev", "", "", "org1", None, "org1"),
        ("dev", "", "org1", None, None, "org1"),
        ("dev", "", "org1", "org2", None, "org2"),
    ],
)
def test_org_id_config_fallback(
    current_context, prod_org_id, dev_org_id, org_id_arg, env_arg, expected, capsys
):
    @org_id_config_fallback
    def command(args: Namespace):
        print(args.org_id)

    config = copy.deepcopy(Configuration.DEFAULT_CONFIG)
    config["auth"]["current_context"] = current_context
    config["auth"]["contexts"]["prod"]["organization_id"] = prod_org_id
    config["auth"]["contexts"]["dev"]["organization_id"] = dev_org_id

    with mock.patch("croud.config.load_config", return_value=config):
        args = Namespace(env=env_arg, org_id=org_id_arg, sudo=False)

        command(args)
        out, _ = capsys.readouterr()
        assert expected in out


def test_org_id_config_fallback_for_sudo(capsys):
    @org_id_config_fallback
    def command(args: Namespace):
        print(args.org_id)

    config = copy.deepcopy(Configuration.DEFAULT_CONFIG)
    config["auth"]["current_context"] = "dev"
    config["auth"]["contexts"]["dev"]["organization_id"] = "some-org-id"

    with mock.patch("croud.config.load_config", return_value=config):
        args = Namespace(env="dev", org_id="some-other-org-id", sudo=True)

        command(args)

        out, _ = capsys.readouterr()
        assert "some-other-org-id" in out


@pytest.mark.parametrize(
    "current_context,prod_org_id,dev_org_id,org_id_arg,env_arg",
    [
        ("dev", "", "", None, None),
        ("prod", "", "org1", None, None),
        ("prod", "", "org1", None, "prod"),
    ],
)
def test_org_id_config_fallback_failed(
    current_context, prod_org_id, dev_org_id, org_id_arg, env_arg, capsys
):
    @org_id_config_fallback
    def command(args: Namespace):
        print(args.org_id)

    config = copy.deepcopy(Configuration.DEFAULT_CONFIG)
    config["auth"]["current_context"] = current_context
    config["auth"]["contexts"]["prod"]["organization_id"] = prod_org_id
    config["auth"]["contexts"]["dev"]["organization_id"] = dev_org_id

    with mock.patch("croud.config.load_config", return_value=config):
        args = Namespace(env=env_arg, org_id=org_id_arg, sudo=False)

        with pytest.raises(SystemExit):
            command(args)


def test_org_id_config_fallback_failed_for_sudo(capsys):
    @org_id_config_fallback
    def command(args: Namespace):
        print(args.org_id)

    config = copy.deepcopy(Configuration.DEFAULT_CONFIG)
    config["auth"]["current_context"] = "dev"
    config["auth"]["contexts"]["dev"]["organization_id"] = "some-org-id"

    with mock.patch("croud.config.load_config", return_value=config):
        args = Namespace(env="dev", org_id=None, sudo=True)

        with pytest.raises(SystemExit):
            command(args)
