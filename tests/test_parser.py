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

import io
from argparse import Namespace
from unittest import mock

import pytest

from croud import __version__
from croud.parser import (
    Argument,
    CroudCliArgumentParser,
    CroudCliHelpFormatter,
    create_parser,
)
from tests.util import assert_ellipsis_match


def noop(args: Namespace):
    pass


class TestParser:
    def test_parser_instance_help(self):
        tree = {"help": "help text", "commands": {}}
        parser = create_parser(tree)

        assert isinstance(parser, CroudCliArgumentParser)
        assert parser.formatter_class == CroudCliHelpFormatter
        assert parser.prog == "croud"
        assert parser.description == "help text"
        assert parser.add_help is False

        fp = io.StringIO()
        parser.print_help(file=fp)
        fp.seek(0)
        usage = fp.read()
        assert "Show this help message and exit." in usage
        assert "Show program's version number and exit." in usage
        assert "Usage: croud" in usage
        assert "Available Commands:" in usage
        assert "Optional Arguments:" in usage
        assert "help text" in usage

    def test_parser_list_commands(self):
        tree = {
            "help": "help text",
            "commands": {
                "cmd_a": {"resolver": noop, "help": "Command A"},
                "cmd_b": {"resolver": noop, "help": "Command B"},
                "cmd_c": {"resolver": noop, "help": "Command C"},
            },
        }
        parser = create_parser(tree)

        fp = io.StringIO()
        parser.print_help(file=fp)
        fp.seek(0)
        usage = fp.read()
        assert_ellipsis_match(
            usage,
            """
Usage: croud [-h] [-v] {cmd_a,cmd_b,cmd_c}
...
Available Commands:
  cmd_a          Command A
  cmd_b          Command B
  cmd_c          Command C
...
""",
        )

    def test_parser_argument_groups(self, capsys):
        tree = {
            "help": "help text",
            "commands": {
                "cmd": {
                    "resolver": noop,
                    "extra_args": [
                        Argument("--arg-a", required=True),
                        Argument("--arg-b", required=False),
                    ],
                    "help": "Command help",
                }
            },
        }
        parser = create_parser(tree)

        with pytest.raises(SystemExit) as ex_info:
            parser.parse_args(["cmd"])
        assert ex_info.value.code == 2
        out, err = capsys.readouterr()

        assert_ellipsis_match(
            out,
            """
Usage: croud cmd [-h] --arg-a ARG_A [--arg-b ARG_B]
...
Required Arguments:
  --arg-a ARG_A
...
Optional Arguments:
...
  --arg-b ARG_B
...
""",
        )
        assert "The following arguments are required: --arg-a" in err

    def test_parser_version(self):
        tree = {"help": "help text", "commands": {}}
        parser = create_parser(tree)

        with mock.patch("sys.stdout.write") as stdout:
            with pytest.raises(SystemExit) as ex_info:
                parser.parse_args(["--version"])
            assert ex_info.value.code == 0
            assert stdout.call_args == mock.call("croud " + __version__ + "\n")

    def test_help(self):
        tree = {"help": "help text", "commands": {}}
        parser = create_parser(tree)
        with mock.patch("sys.stdout.write") as stdout:
            with pytest.raises(SystemExit) as ex_info:
                parser.parse_args(["--help"])
                stdout.assert_called_once()
                assert stdout.call_args[0][0].startswith("Usage: croud") is True
        assert ex_info.value.code == 0

    def test_no_args(self):
        tree = {"help": "help text", "commands": {}}
        parser = create_parser(tree)
        args = parser.parse_args([])
        assert args.resolver.__name__ == "print_help"

    def test_commands_without_args(self):
        tree = {"help": "help text", "commands": {"cmd": {"resolver": noop}}}
        parser = create_parser(tree)

        argv = ["cmd"]
        args = parser.parse_args(argv)
        assert args.resolver == noop
        assert args == Namespace(
            output_fmt=None, region=None, sudo=False, resolver=noop
        )

    def test_commands_with_args(self):
        tree = {
            "help": "help text",
            "commands": {
                "cmd": {
                    "resolver": noop,
                    "extra_args": [
                        Argument("-a", type=int, required=True),
                        Argument("-b", type=str, required=False),
                    ],
                }
            },
        }
        parser = create_parser(tree)

        argv = ["cmd", "-a", "1", "-b", "foo"]
        args = parser.parse_args(argv)
        assert args.resolver == noop
        assert "a" in args
        assert "b" in args

    def test_commands_with_subcommands(self):
        tree = {
            "help": "help text",
            "commands": {
                "cmd": {
                    "commands": {
                        "list": {
                            "resolver": noop,
                            "extra_args": [
                                Argument("-a", type=int, required=True),
                                Argument("-b", type=str, required=False),
                            ],
                        }
                    }
                }
            },
        }
        parser = create_parser(tree)

        argv = ["cmd", "list", "-a", "1", "-b", "foo"]
        args = parser.parse_args(argv)
        assert args.resolver == noop
        assert "a" in args
        assert "b" in args

    def test_default_arguments(self):
        tree = {"help": "help text", "commands": {"cmd": {"resolver": noop}}}
        parser = create_parser(tree)

        argv = [
            "cmd",
            "--region",
            "eastus.azure",
            "--output-fmt",
            "json",
        ]
        args = parser.parse_args(argv)
        assert args.region == "eastus.azure"
        assert args.output_fmt == "json"

    def test_default_sudo_argument(self):
        tree = {"help": "help text", "commands": {"cmd": {"resolver": noop}}}
        parser = create_parser(tree)

        argv = ["cmd", "--sudo"]
        args = parser.parse_args(argv)
        assert args.sudo is True
