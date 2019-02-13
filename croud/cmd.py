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
from argparse import ArgumentParser, Namespace, _ArgumentGroup, _SubParsersAction
from os.path import basename
from typing import Callable, Dict, List, Optional, Tuple

from croud import __version__

POSITIONALS_TITLE = "Available Commands"
REQUIRED_TITLE = "Required Arguments"
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
    def __init__(self, tree: Dict) -> None:
        self.cmd_tree = tree

    def _create_root_parser(self) -> CroudCliArgumentParser:
        parser = CroudCliArgumentParser(
            prog="croud",
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
        return parser

    def _create_parent_cmd(
        self,
        depth: int,
        argv: List[str],
        commands: dict,
        parent_parser: Optional[CroudCliArgumentParser] = None,
    ):
        parser = parent_parser or self._create_root_parser()
        subparser = parser.add_subparsers()

        try:
            context_name = argv[depth]
        except IndexError:
            context_name = argv[depth - 1]
        context_name = basename(context_name)

        context: Optional[ArgumentParser] = None
        resolver: Optional[Callable] = None

        for key, command in commands.items():
            subparser.add_parser(key, help=command.get("help"))

            if key == context_name:
                context = CroudCliArgumentParser(
                    formatter_class=CroudCliHelpFormatter, add_help=False
                )
                context._positionals.title = POSITIONALS_TITLE

                req_args = context.add_argument_group(REQUIRED_TITLE)
                opt_args = context.add_argument_group(OPTIONALS_TITLE)
                opt_args.add_argument(
                    "-h",
                    "--help",
                    action="help",
                    default=argparse.SUPPRESS,
                    help="Show this help message and exit.",
                )

                if "noop_arg" in command:
                    cmd = command["noop_arg"]
                    context.add_argument(key, choices=cmd["choices"])
                    resolver = command["calls"]
                    break

                if "extra_args" in command:
                    for arg_def in command["extra_args"]:
                        arg_def(req_args, opt_args)

                if "sub_commands" in command:
                    return self._create_parent_cmd(
                        depth + 1, argv, command["sub_commands"], parent_parser=context
                    )
                else:
                    add_default_args(opt_args)
                    resolver = command["calls"]
                break

        cmd_args = argv[depth : depth + 1]
        if context:
            # supported subcommand used
            try:
                format_usage(context, depth + 1)
            except UnboundLocalError:
                format_usage(parser, depth + 1)
                parser.print_help()
                exit(1)
            parser.parse_args(cmd_args)
            return resolver, context.parse_args(argv[depth + 1 :])
        else:
            # command has no parent parser
            if cmd_args:
                format_usage(parser, depth + 1, cmd_args)
                # root level argument (e.g. --version)
                parser.parse_args(cmd_args)
            else:
                format_usage(parser, depth + 1)
                # show help if no argument passed at all
                parser.print_help()
        return (None, None)

    def resolve(self, argv) -> Tuple[Optional[Callable], Namespace]:
        return self._create_parent_cmd(1, argv, self.cmd_tree)


def add_default_args(opt_args: _ArgumentGroup) -> None:
    env_arg(opt_args)


def env_arg(opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument(
        "--env",
        choices=["prod", "dev"],
        default=None,
        type=str,
        help="Switches auth context.",
    )


def region_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument(
        "-r",
        "--region",
        choices=["westeurope.azure", "eastus.azure", "eastus2.azure", "bregenz.a1"],
        type=str,
        help="Switch region that command will be run on.",
        required=False,
    )


def project_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "-p", "--project-id", type=str, help="Project ID.", required=required
    )


def project_name_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument("--name", type=str, help="Project Name.", required=True)


def output_fmt_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument(
        "-o",
        "--output-fmt",
        choices=["table", "json"],
        type=str,
        help="Switches output format.",
    )


def org_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument("--org-id", type=str, help="Organization ID.", required=required)


def no_org_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument(
        "--no-org",
        nargs="?",
        default=False,
        const=True,
        type=bool,
        help="Only show users that are not part of any organization.",
    )


def org_name_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument("--name", type=str, help="Organization Name.", required=True)


def org_plan_type_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--plan-type",
        choices=[1, 2, 3, 4, 5, 6],
        type=int,
        help="Plan type for organization.",
        required=True,
    )


def resource_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument("--resource", type=str, help="Resource ID.", required=required)


def role_fqn_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--role",
        type=str,
        help="Role FQN. Run `croud roles list` for a list of available roles.",
        required=required,
    )


def user_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument("--user", type=str, help="User ID.", required=required)


def user_id_or_email_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--user", type=str, help="User email address or ID", required=True
    )


def cluster_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--cluster-id", type=str, help="CrateDB cluster ID", required=required
    )


def product_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument("--product-id", type=str, help="Filter by product ID.")


def product_tier_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument("--tier", type=str, help="Product Tier.", required=True)


def product_unit_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument("--unit", type=int, help="Product Scale Unit.", required=True)


def product_name_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--product-name", type=str, help="Name of the product.", required=True
    )


def crate_version_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument("--version", type=str, help="CrateDB version.", required=True)


def crate_username_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--username", type=str, help="CrateDB username.", required=True
    )


def crate_password_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--password", type=str, help="CrateDB password.", required=True
    )


def consumer_set_id_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--consumer-set-id",
        type=str,
        help="The identifier of the consumer set",
        required=True,
    )


def consumer_eventhub_connection_string_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-eventhub-connection-string",
        type=str,
        help="Connection string of the EventHub from which to consume.",
        required=required,
    )


def consumer_eventhub_consumer_group_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-eventhub-consumer-group",
        type=str,
        help="EventHub Consumer Group from which to consume.",
        required=required,
    )


def consumer_eventhub_lease_storage_connection_string_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-eventhub-lease-storage-connection-string",
        type=str,
        help="Connection string of the lease storage for the EventHub consumer.",
        required=required,
    )


def consumer_eventhub_lease_storage_container_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-eventhub-lease-storage-container",
        type=str,
        help="Container of the lease storage for the EventHub consumer.",
        required=required,
    )


def consumer_schema_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-schema",
        type=str,
        help="Database schema in which to insert.",
        required=required,
    )


def consumer_table_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-table",
        type=str,
        help="Database table in which to insert.",
        required=required,
    )


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
