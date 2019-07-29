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

import abc
import functools
import json
import sys
from typing import Any, Callable, Dict, List, Optional, Type, Union

import yaml
from colorama import Fore, Style
from tabulate import tabulate

from croud.typing import JsonDict

print_stderr = functools.partial(print, file=sys.stderr)


def print_format(
    rows: Union[List[JsonDict], JsonDict],
    format: str,
    keys: Optional[List[str]] = None,
    transforms: List[Optional[Callable[[Any], Any]]] = None,
) -> None:
    try:
        Printer = PRINTERS[format]
    except KeyError:
        print_error("This print method is not supported.")
        exit(1)
    printer = Printer(keys, transforms)
    printer.print_rows(rows)


def print_response(
    data,
    errors,
    output_fmt,
    success_message: str = None,
    keys: List[str] = None,
    transforms: List[Optional[Callable[[Any], Any]]] = None,
):
    if errors:
        if "message" in errors:
            print_error(errors["message"])
            if "errors" in errors:
                print_format(errors["errors"], "json")
        else:
            print_format(errors, "json")
        return

    if data is None:
        message = success_message or "Success."
        print_success(message)
        return

    print_format(data, output_fmt, keys, transforms)

    if data and success_message is not None:
        message = success_message
        print_success(message)


def print_error(text: str):
    print_stderr(Fore.RED + "==> Error: " + Style.RESET_ALL + text, file=sys.stderr)


def print_info(text: str):
    print_stderr(Fore.CYAN + "==> Info: " + Style.RESET_ALL + text, file=sys.stderr)


def print_warning(text: str):
    print_stderr(
        Fore.YELLOW + "==> Warning: " + Style.RESET_ALL + text, file=sys.stderr
    )


def print_success(text: str):
    print_stderr(Fore.GREEN + "==> Success: " + Style.RESET_ALL + text, file=sys.stderr)


class FormatPrinter(abc.ABC):
    def __init__(
        self,
        keys: Optional[List[str]] = None,
        transforms: List[Optional[Callable[[Any], Any]]] = None,
    ):
        assert not transforms or transforms and keys and len(keys) == len(transforms), (
            "When providing transforms the number of transforms must match the number "
            "of provided keys."
        )

        self.keys = keys
        self.transforms = transforms

    def print_rows(self, rows: Union[List[JsonDict], JsonDict]) -> None:
        print(self.format_rows(rows))

    @abc.abstractmethod
    def format_rows(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        raise NotImplementedError()


class JsonFormatPrinter(FormatPrinter):
    def format_rows(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        return json.dumps(rows, sort_keys=False, indent=2)


class TableFormatPrinter(FormatPrinter):
    transform_funcs: Dict[str, Callable[[Any], Any]] = {}

    def __init__(
        self,
        keys: Optional[List[str]] = None,
        transforms: List[Optional[Callable[[Any], Any]]] = None,
    ):
        super().__init__(keys=keys, transforms=transforms)
        if keys and transforms:
            self.transform_funcs = {
                key: transform or TableFormatPrinter._identity_transform
                for key, transform in zip(keys, transforms)
            }

    def format_rows(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        if rows is None:
            return ""

        if not isinstance(rows, list):
            rows = [rows]

        if self.keys:
            filter_record = functools.partial(self._filter_record, keys=self.keys)
            rows = list(map(filter_record, rows))

        # ensure that keys are mapped to their values
        # e.g. Rows, generated with
        # [{"a": "foo", "b": 1}, {"b": 2, "a": "bar"}]
        # should get printed same as
        # [{"a": "foo", "b": 1}, {"a": "bar", "b": "1"}]
        # +-----+-----+
        # | a   |   b |
        # |-----+-----|
        # | foo |   1 |
        # |-----+-----|
        # | bar |   2 |
        # +-----+-----+

        headers = list(map(str, rows[0].keys())) if len(rows) else self.keys
        if headers is None:
            return ""
        values = [
            [
                self.transform_funcs.get(
                    header, TableFormatPrinter._identity_transform
                )(row[header])
                for header in headers
            ]
            for row in rows
        ]

        return tabulate(values, headers=headers, tablefmt="psql", missingval="NULL")

    def _filter_record(self, data: dict, keys: List[str]) -> JsonDict:
        return {key: value for key, value in data.items() if key in keys}

    @staticmethod
    def _identity_transform(field):
        """transform field for displaying"""
        if isinstance(field, (list, dict)):
            return json.dumps(field, sort_keys=True, ensure_ascii=False)
        elif isinstance(field, bool):
            return "TRUE" if field else "FALSE"
        else:
            return field


class YamlFormatPrinter(FormatPrinter):
    def format_rows(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        return yaml.dump(rows, default_flow_style=False)


PRINTERS: Dict[str, Type[FormatPrinter]] = {
    "json": JsonFormatPrinter,
    "table": TableFormatPrinter,
    "yaml": YamlFormatPrinter,
}
