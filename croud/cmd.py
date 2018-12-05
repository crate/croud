import argparse
import sys
from argparse import ArgumentParser, Namespace
from typing import Callable

from croud import __version__


class CMD:
    def __init__(self, commands: dict):
        parser: ArgumentParser = argparse.ArgumentParser(
            usage="A command line interface for CrateDB Cloud"
        )
        parser.add_argument(
            "-v", "--version", action="version", version="%(prog)s " + __version__
        )

        self.create_parent_cmd(parser, 1, commands)

    def create_parent_cmd(self, parser: ArgumentParser, depth: int, commands: dict):
        subparser = parser.add_subparsers()
        context: ArgumentParser
        call: Callable

        try:
            context_name = sys.argv[depth]
        except IndexError:
            context_name = sys.argv[depth - 1]

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
                    self.create_parent_cmd(context, depth + 1, command["sub_commands"])
                    return
                else:
                    add_default_args(context)
                    call = command["calls"]
                break

        try:
            format_usage(context, depth + 1)
        except UnboundLocalError:
            format_usage(parser, depth + 1)
            parser.print_help()
            exit(1)

        parser.parse_args(sys.argv[depth : depth + 1])
        call(parse_args(context, depth + 1))


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


def output_fmt_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-o",
        "--output-fmt",
        choices=["json"],
        default="json",
        type=str,
        help="Switches output format",
    )


def format_usage(parser: ArgumentParser, depth: int) -> None:
    usage = parser.format_usage()
    args = list(filter(lambda arg: arg != "-h" and arg != "--help", sys.argv[:depth]))
    args[0] = "croud"

    nusg = " ".join(args)
    parser.usage = usage.replace("usage: croud", nusg, 1)
