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
from argparse import ArgumentParser, Namespace
from typing import Callable, Optional

from croud import __version__


class CMD:
    def __init__(self):
        parser: ArgumentParser = argparse.ArgumentParser(
            usage="A command line interface for CrateDB Cloud"
        )
        parser.add_argument(
            "-v", "--version", action="version", version="%(prog)s " + __version__
        )
        self.root_parser = parser

    def create_parent_cmd(
        self, depth: int, commands: dict, parent_parser: Optional[ArgumentParser] = None
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

        context: Optional[ArgumentParser] = None
        call: Callable
        for key, command in commands.items():
            subparser.add_parser(key)
            if key == context_name:
                context = argparse.ArgumentParser()
                if "description" in command:
                    context.description = command["description"]

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
                # root level argument (e.g. --version)
                parser.parse_args(cmd_args)
            else:
                # show help if no argument passed at all
                parser.print_help()


def parse_args(parser: ArgumentParser, position: int) -> Namespace:
    args = parser.parse_args(sys.argv[position:])
    return args


def add_default_args(parser: ArgumentParser) -> None:
    env_arg(parser)


def env_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--env",
        choices=["prod", "dev"],
        default=None,
        type=str,
        help="Switches auth context",
    )


def region_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-r",
        "--region",
        choices=["westeurope.azure", "eastus.azure", "bregenz.a1"],
        default="bregenz.a1",
        type=str,
        help="Switch region that command will be run on",
    )


def project_id_arg(parser: ArgumentParser) -> None:
    parser.add_argument("-p", "--project-id", type=str, help="Filter by project ID")


def output_fmt_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-o",
        "--output-fmt",
        choices=["table", "json"],
        default="table",
        type=str,
        help="Switches output format",
    )


def format_usage(parser: ArgumentParser, depth: int) -> None:
    usage = parser.format_usage()
    args = list(filter(lambda arg: arg != "-h" and arg != "--help", sys.argv[:depth]))
    args[0] = "croud"

    nusg = " ".join(args)
    parser.usage = usage.replace("usage: croud", nusg, 1)
