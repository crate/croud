#!/usr/bin/env python
#
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

import argparse
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction
from os.path import basename
from typing import Callable, Optional

from croud import __version__

POSITIONALS_TITLE = "Available Commands"
OPTIONALS_TITLE = "Optional Arguments"


class CroudCliArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"{message.capitalize()}\n\n")
        self.print_help()
        sys.exit(2)


class CroudCliHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        result = super()._format_action(action)
        if isinstance(action, _SubParsersAction):
            # Remove empty line
            return "%*s%s" % (self._current_indent, "", result.lstrip())
        return result

    def _format_action_invocation(self, action):
        if isinstance(action, _SubParsersAction):
            # Remove metavar {command}
            return ""
        return super()._format_action_invocation(action)

    def _iter_indented_subactions(self, action):
        if isinstance(action, _SubParsersAction):
            try:
                get_subactions = action._get_subactions
            except AttributeError:
                pass
            else:
                # Remove indentation
                yield from get_subactions()
        else:
            yield from super()._iter_indented_subactions(action)

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "Usage: "

        return super(CroudCliHelpFormatter, self).add_usage(
            usage, actions, groups, prefix
        )


class CMD:
    def __init__(self):
        parser: CroudCliArgumentParser = CroudCliArgumentParser(
            description="A command line interface for CrateDB Cloud.",
            usage="croud [subcommand] {parameters}",
            formatter_class=CroudCliHelpFormatter,
            add_help=False,
        )
        parser._positionals.title = POSITIONALS_TITLE
        parser._optionals.title = OPTIONALS_TITLE
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + __version__,
            help="Show program's version number and exit.",
        )
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )
        self.root_parser = parser

    def create_parent_cmd(
        self,
        depth: int,
        commands: dict,
        parent_parser: Optional[CroudCliArgumentParser] = None,
    ):
        parser = self.root_parser
        if parent_parser:
            # a parent parser exists, so use it to parse it's subcommand(s)
            parser = parent_parser

        subparser = parser.add_subparsers()

        try:
            context_name = sys.argv[depth]
        except IndexError:
            context_name = sys.argv[depth - 1]
        context_name = basename(context_name)

        context: Optional[ArgumentParser] = None
        call: Callable
        for key, command in commands.items():
            subparser.add_parser(key, help=command.get("help"))

            if key == context_name:
                context = CroudCliArgumentParser(
                    formatter_class=CroudCliHelpFormatter, add_help=False
                )
                context._positionals.title = POSITIONALS_TITLE
                context._optionals.title = OPTIONALS_TITLE
                context.add_argument(
                    "-h",
                    "--help",
                    action="help",
                    default=argparse.SUPPRESS,
                    help="Show this help message and exit.",
                )

                if "noop_arg" in command:
                    cmd = command["noop_arg"]
                    context.add_argument(key, choices=cmd["choices"])
                    call = command["calls"]
                    break

                if "extra_args" in command:
                    for arg_def in command["extra_args"]:
                        arg_def(context)

                if "sub_commands" in command:
                    self.create_parent_cmd(
                        depth + 1, command["sub_commands"], parent_parser=context
                    )
                    return
                else:
                    add_default_args(context)
                    call = command["calls"]
                break

        cmd_args = sys.argv[depth : depth + 1]
        if context:
            # supported subcommand used
            try:
                format_usage(context, depth + 1)
            except UnboundLocalError:
                format_usage(parser, depth + 1)
                parser.print_help()
                exit(1)
            parser.parse_args(cmd_args)
            call(parse_args(context, depth + 1))
        else:
            if cmd_args:
                format_usage(parser, depth + 1, cmd_args)
                # root level argument (e.g. --version)
                parser.parse_args(cmd_args)
            else:
                format_usage(parser, depth + 1)
                # show help if no argument passed at all
                parser.print_help()


def parse_args(parser: ArgumentParser, position: int) -> Namespace:
    return parser.parse_args(sys.argv[position:])


def add_default_args(parser: ArgumentParser) -> None:
    env_arg(parser)


def env_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--env",
        choices=["prod", "dev"],
        default=None,
        type=str,
        help="Switches auth context.",
    )


def region_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-r",
        "--region",
        choices=["westeurope.azure", "eastus.azure", "bregenz.a1"],
        type=str,
        help="Switch region that command will be run on.",
    )


def project_id_arg(parser: ArgumentParser) -> None:
    parser.add_argument("-p", "--project-id", type=str, help="Filter by project ID.")


def output_fmt_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-o",
        "--output-fmt",
        choices=["table", "json"],
        type=str,
        help="Switches output format.",
    )


def org_name_arg(parser: ArgumentParser) -> None:
    parser.add_argument("--name", type=str, help="Organization Name.", required=True)


def org_plan_type_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--plan-type",
        choices=[1, 2, 3, 4, 5, 6],
        type=int,
        help="Plan type for organization.",
        required=True,
    )


def resource_id_arg(parser: ArgumentParser, required: bool) -> None:
    parser.add_argument("--resource", type=str, help="Resource ID.", required=required)


def role_fqn_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--role",
        type=str,
        help="Role FQN. Run `croud roles list` for a list of available roles.",
        required=True,
    )


def user_id_arg(parser: ArgumentParser, required: bool) -> None:
    parser.add_argument("--user", type=str, help="User ID.", required=required)


def format_usage(parser: ArgumentParser, depth: int, invalid_args=None) -> None:
    usage = parser.format_usage()
    args = list(filter(lambda arg: arg != "-h" and arg != "--help", sys.argv[:depth]))
    args[0] = parser.prog

    if invalid_args:
        invalid_args = " ".join(invalid_args)
        if invalid_args in args:
            args.remove(invalid_args)
    nusg = " ".join(args)
    parser.usage = usage.replace(f"Usage: {parser.prog}", nusg, 1)
