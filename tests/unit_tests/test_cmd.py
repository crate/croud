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

import pytest

from croud import __version__
from croud.cmd import CMD, region_arg


def print_hello(args: Namespace):
    print("Hello!")


def print_env(args: Namespace):
    print(args.env)


def print_region(args: Namespace):
    print(args.region)


class TestCmd:
    commands = {
        "say-hi": {"calls": print_hello},
        "print-env": {"calls": print_env},
        "print-region": {"extra_args": [region_arg], "calls": print_region},
        "print": {"sub_commands": {"hello": {"calls": print_hello}}},
    }

    def test_commands_registered(self):
        argv = ["croud", "say-hi"]
        croud_cmd = CMD(self.commands)
        func, args = croud_cmd.resolve(argv)

        assert func == print_hello
        assert args == Namespace(env=None)

    def test_commands_have_env_arg(self):
        argv = ["croud", "print-env", "--env", "dev"]
        croud_cmd = CMD(self.commands)
        func, args = croud_cmd.resolve(argv)

        assert func == print_env
        assert args == Namespace(env="dev")

    def test_extra_args_registered(self):
        argv = ["croud", "print-region", "--region", "westeurope.azure"]
        croud_cmd = CMD(self.commands)
        func, args = croud_cmd.resolve(argv)

        assert func == print_region
        assert args == Namespace(env=None, region="westeurope.azure")

    def test_sub_commands_registered(self):
        argv = ["croud", "print", "hello"]
        croud_cmd = CMD(self.commands)
        func, args = croud_cmd.resolve(argv)

        assert func == print_hello
        assert args == Namespace(env=None)

    def test_version(self):
        argv = ["croud", "--version"]
        croud_cmd = CMD(self.commands)

        with mock.patch("sys.stdout.write") as stdout:
            with pytest.raises(SystemExit) as ex_info:
                croud_cmd.resolve(argv)
            assert ex_info.value.code == 0
            assert stdout.call_args == mock.call("croud " + __version__ + "\n")

    def test_no_args(self):
        argv = ["croud"]
        croud_cmd = CMD(self.commands)
        with mock.patch("sys.stdout.write") as stdout:
            fn, args = croud_cmd.resolve(argv)
            assert fn is None
            assert args is None
            stdout.assert_called_once()
            assert stdout.call_args[0][0].startswith("Usage: croud") is True

    def test_help(self):
        argv = ["croud", "--help"]
        croud_cmd = CMD(self.commands)
        with mock.patch("sys.stdout.write") as stdout:
            with pytest.raises(SystemExit) as ex_info:
                croud_cmd.resolve(argv)
                stdout.assert_called_once()
                assert stdout.call_args[0][0].startswith("Usage: croud") is True
        assert ex_info.value.code == 0
