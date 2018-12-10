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

import sys
import unittest
from argparse import Namespace
from unittest import mock

from croud.cmd import CMD, region_arg


def print_hello(args: Namespace):
    print("Hello!")


def print_env(args: Namespace):
    print(args.env)


def print_region(args: Namespace):
    print(args.region)


class TestCmd(unittest.TestCase):
    commands: dict = {
        "say-hi": {"calls": print_hello},
        "print-env": {"calls": print_env},
        "print-region": {"extra_args": [region_arg], "calls": print_region},
        "print": {"sub_commands": {"hello": {"calls": print_hello}}},
    }

    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_commands_registered(self, mock_print):
        sys.argv = ["croud", "say-hi"]
        croud_cmd = CMD()
        croud_cmd.create_parent_cmd(1, self.commands)

        mock_print.assert_called_once_with("Hello!")

    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_commands_have_env_arg(self, mock_print):
        sys.argv = ["croud", "print-env", "--env", "dev"]
        croud_cmd = CMD()
        croud_cmd.create_parent_cmd(1, self.commands)

        mock_print.assert_called_once_with("dev")

    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_extra_args_registered(self, mock_print):
        sys.argv = ["croud", "print-region", "--region", "westeurope.azure"]
        croud_cmd = CMD()
        croud_cmd.create_parent_cmd(1, self.commands)

        mock_print.assert_called_once_with("westeurope.azure")

    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_sub_commands_registered(self, mock_print):
        sys.argv = ["croud", "print", "hello"]
        croud_cmd = CMD()
        croud_cmd.create_parent_cmd(1, self.commands)

        mock_print.assert_called_once_with("Hello!")

    def test_version(self):
        sys.argv = ["croud", "--version"]
        croud_cmd = CMD()
        with mock.patch.object(croud_cmd.root_parser, "parse_args") as mock_parser:
            croud_cmd.create_parent_cmd(1, self.commands)
            mock_parser.assert_called_once_with(["--version"])

    def test_no_args(self):
        sys.argv = ["croud"]
        croud_cmd = CMD()
        with mock.patch.object(croud_cmd.root_parser, "print_help") as mock_help:
            croud_cmd.create_parent_cmd(1, self.commands)
            mock_help.assert_called_once()
