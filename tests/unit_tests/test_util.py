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

import unittest
from argparse import Namespace
from unittest import mock

import pytest

from croud.util import (
    can_launch_browser,
    clean_dict,
    confirm_prompt,
    get_platform_info,
    is_wsl,
    open_page_in_browser,
    require_confirmation,
)


class TestUtils(unittest.TestCase):
    authd_mutation = {"mutationName": {"prop1": "propvalue"}}
    unauthd_mutation = {"errors": [{"message": "An error message"}]}
    authd_entity_list = {"entityListName": {"data": [{"key": "value"}]}}

    # This function was copied from the <https://github.com/Azure/azure-cli>
    # project. See `LICENSE` for more information.
    @mock.patch("webbrowser.open", autospec=True)
    @mock.patch("subprocess.call", autospec=True)
    def test_open_page_in_browser(self, subprocess_call_mock, webbrowser_open_mock):
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
    def test_can_launch_browser(self, webbrowser_get_mock, get_platform_mock):
        # WSL is always fine
        get_platform_mock.return_value = ("linux", "4.4.0-17134-microsoft")
        result = can_launch_browser()
        self.assertTrue(result)

        # windows is always fine
        get_platform_mock.return_value = ("windows", "10")
        result = can_launch_browser()
        self.assertTrue(result)

        # osx is always fine
        get_platform_mock.return_value = ("darwin", "10")
        result = can_launch_browser()
        self.assertTrue(result)

        # now tests linux
        with mock.patch("os.environ", autospec=True) as env_mock:
            # when no GUI, return false
            get_platform_mock.return_value = ("linux", "4.15.0-1014-azure")
            env_mock.get.return_value = None
            result = can_launch_browser()
            self.assertFalse(result)

            # when there is gui, and browser is a good one, return True
            browser_mock = mock.MagicMock()
            browser_mock.name = "goodone"
            env_mock.get.return_value = "foo"
            result = can_launch_browser()
            self.assertTrue(result)

            # when there is gui, but the browser is text mode, return False
            browser_mock = mock.MagicMock()
            browser_mock.name = "www-browser"
            webbrowser_get_mock.return_value = browser_mock
            env_mock.get.return_value = "foo"
            result = can_launch_browser()
            self.assertFalse(result)


@pytest.mark.parametrize(
    ["raw", "cleaned"],
    [
        ({}, {}),
        (
            {"int": 0, "str": "", "none": None, "list": []},
            {"int": 0, "str": "", "list": []},
        ),
        (
            {"empty": {}, "nested": {"value": 42, "none": None}},
            {"empty": {}, "nested": {"value": 42}},
        ),
    ],
)
def test_clean_dict(raw, cleaned):
    assert clean_dict(raw) == cleaned


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

    out, _ = capsys.readouterr()
    assert output in out
