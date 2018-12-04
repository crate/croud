import argparse
import sys

from argparse import ArgumentParser
from argparse import Namespace
from croud.login import login
from croud.logout import logout
from croud.me import me
from croud.projects.list import projects_list


class CMD:
    def __init__(self):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()

        context_name = sys.argv[1]
        context: ArgumentParser
        has_defaults: bool = True
        commands: dict = {
            "me": {
                "description": "Prints the current logged in user",
                "usage": "croud me [-h] [--env {prod,dev}]\n\t\t"
                         "[-r {westeurope.azure,eastus.azure,bregenz.a1}] "
                         "[-o {json}]"
            },
            "login": {
                "description": "Performs an OAuth2 Login to CrateDB Cloud",
                "usage": "croud login [-h] [--env {prod,dev}]"
            },
            "logout": {
                "description": "Performs a logout of the current logged in user",
                "usage": "croud logout [-h] [--env {prod,dev}]"
            },
            "projects": {
                "description": "Project sub commands",
                "usage": "croud projects [-h] {list,create}",
                "sub_command": True
            }
        }

        for key, command in commands.items():
            subparser.add_parser(key)
            if key == context_name:
                context = argparse.ArgumentParser(
                    description=command["description"],
                    usage=command["usage"]
                )
                has_defaults = "sub_command" not in command

        parser.parse_args(sys.argv[1:2])

        if has_defaults:
            add_default_args(context)

        getattr(self, sys.argv[1])(context)

    def me(self, parser: ArgumentParser):
        add_region_arg(parser)
        add_output_fmt_arg(parser)

        me(parse_args(parser, 2))

    def login(self, parser):
        login(parse_args(parser, 2))

    def logout(self, parser):
        logout(parse_args(parser, 2))

    def projects(self, parser):
        subparsers: [str] = ["list"]
        subparser = parser.add_subparsers()

        for sp in subparsers:
            subparser.add_parser(sp)

        if len(sys.argv) < 3:
            parser.print_help()
            sys.exit(1)

        parser.parse_args(sys.argv[2:3])
        getattr(self, f"projects_{sys.argv[2]}")()


    def projects_list(self):
        parser = argparse.ArgumentParser(
            description="Lists all projects for the current user in the specified region",
            usage="croud projects list [-h] [--env {prod,dev}] [-o {json}]"
        )

        add_default_args(parser)
        add_output_fmt_arg(parser)

        projects_list(parse_args(parser, 3))


def parse_args(parser: ArgumentParser, position: int) -> Namespace:
    args = parser.parse_args(sys.argv[position:])

    return args


def add_default_args(parser: ArgumentParser) -> None:
    add_env_arg(parser)


def add_env_arg(parser: ArgumentParser):
    parser.add_argument(
        "--env",
        choices=["prod", "dev"],
        default=None,
        type=str,
        help="Switches auth context"
    )


def add_region_arg(parser: ArgumentParser):
    parser.add_argument(
        "-r", "--region",
        choices=["westeurope.azure", "eastus.azure", "bregenz.a1"],
        default="bregenz.a1",
        type=str,
        help="Switch region that command will be run on"
    )


def add_output_fmt_arg(parser: ArgumentParser):
    parser.add_argument(
        "-o",
        "--output-fmt",
        choices=["json"],
        default="json",
        type=str,
        help="Switches output format"
    )