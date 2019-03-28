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
from croud.parser import CroudCliArgumentParser, CroudCliHelpFormatter, create_parser


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
        command_list = """Available Commands:
  cmd_a          Command A
  cmd_b          Command B
  cmd_c          Command C

"""
        assert command_list in usage

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
        assert args == Namespace(env=None, output_fmt=None, region=None, resolver=noop)

    def test_commands_with_args(self):
        tree = {
            "help": "help text",
            "commands": {
                "cmd": {
                    "resolver": noop,
                    "extra_args": [
                        lambda a, b: a.add_argument("-a", type=int, required=True),
                        lambda a, b: b.add_argument("-b", type=str, required=False),
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
                                lambda a, b: a.add_argument(
                                    "-a", type=int, required=True
                                ),
                                lambda a, b: b.add_argument(
                                    "-b", type=str, required=False
                                ),
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
            "--env",
            "local",
            "--output-fmt",
            "json",
        ]
        args = parser.parse_args(argv)
        assert args.env == "local"
        assert args.region == "eastus.azure"
        assert args.output_fmt == "json"
