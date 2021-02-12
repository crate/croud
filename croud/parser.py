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
import functools
import inspect
import sys
from typing import Set

from croud import __version__
from croud.config.schemas import OUTPUT_FORMATS
from croud.tools.spinner import HALO

POSITIONALS_TITLE = "Available Commands"
REQUIRED_TITLE = "Required Arguments"
OPTIONALS_TITLE = "Optional Arguments"


class Argument:
    """
    An :class:`argparse.ArgumentParser` argument class.

    Create an instance of it with the positional and keyword arguments usually
    passed to :meth:`~argparse.ArgumentParser.add_argument`. When calling
    :meth:`add_to_parser` with a parser instance, the positional and keyword
    arguments will be passed as-is::

        >>> import argparse
        >>> argument = Argument("integer", type=int)
        >>> parser = argparse.ArgumentParser()
        >>> argument.add_to_parser(parser)
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser: argparse._ActionsContainer):
        parser.add_argument(*self.args, **self.kwargs)

    @property
    def required(self):
        return self.kwargs.get("required", False)

    @property
    def positional(self):
        # This check is not very safe, since the argument prefix could be
        # changed and be something like `+` or any other character.
        # However, since we use `-` as prefix for arguments, it's OK.
        return not self.args[0].startswith("-")


class CroudCliArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(
            formatter_class=CroudCliHelpFormatter, add_help=False, **kwargs
        )
        self._positionals.title = POSITIONALS_TITLE
        self._optionals.title = OPTIONALS_TITLE

        self._group_required = self.add_argument_group(REQUIRED_TITLE)
        self._group_optional = self.add_argument_group(OPTIONALS_TITLE)
        self._group_optional.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )

    def error(self, message):
        sys.stderr.write(f"{message.capitalize()}\n\n")
        self.print_help()
        sys.exit(2)


class CroudCliHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        result = super()._format_action(action)
        if isinstance(action, argparse._SubParsersAction):
            # Remove empty line
            return "%*s%s" % (self._current_indent, "", result.lstrip())
        return result

    def _format_action_invocation(self, action):
        if isinstance(action, argparse._SubParsersAction):
            # Remove metavar {command}
            return ""
        return super()._format_action_invocation(action)

    def _iter_indented_subactions(self, action):
        if isinstance(action, argparse._SubParsersAction):
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


def add_default_args(parser, omit: Set[str]):
    if "region" not in omit:
        parser._group_optional.add_argument(
            "--region",
            "-r",
            required=False,
            help="Temporarily use the specified region that command will be run in.",
        )
    if "format" not in omit:
        parser._group_optional.add_argument(
            "--output-fmt",
            "--format",
            "-o",
            required=False,
            choices=OUTPUT_FORMATS,
            help="Change the formatting of the output.",
        )
    if "sudo" not in omit:
        parser._group_optional.add_argument(
            "--sudo",
            required=False,
            action="store_true",
            help="Run the given command as superuser.",
        )


def help_print_factory(parser: argparse.ArgumentParser):
    def print_help(*args, **kwargs):
        # Need to explicitly stop the spinner here as this is not going through
        # the standard printer
        HALO.stop()
        parser.print_help()

    return print_help


def add_subparser(parser, tree, name="__root__"):
    if "extra_args" in tree:
        for argument in tree["extra_args"]:
            if argument.required or argument.positional:
                argument.add_to_parser(parser._group_required)
            else:
                argument.add_to_parser(parser._group_optional)
    if "noop_arg" in tree:
        parser.add_argument(name.split(" ")[-1], choices=tree["noop_arg"]["choices"])
    if "commands" in tree:
        parser.set_defaults(resolver=help_print_factory(parser))
        subparsers = parser.add_subparsers()
        for _cmd, _tree in tree["commands"].items():
            sub = subparsers.add_parser(_cmd, help=_tree.get("help"))
            add_subparser(sub, _tree, sub.prog)
    if "resolver" in tree:
        add_default_args(parser, omit=tree.get("omit", set([])))
        resolver = tree["resolver"]
        signature = inspect.signature(resolver)
        if "parser" in signature.parameters:
            resolver = functools.partial(resolver, parser=parser)
        parser.set_defaults(resolver=resolver)


def create_parser(tree):
    parser = CroudCliArgumentParser(prog="croud", description=tree["help"])
    parser._group_optional.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="Show program's version number and exit.",
    )
    add_subparser(parser, tree, parser.prog)
    return parser
