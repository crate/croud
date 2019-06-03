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
from typing import Dict, List, Optional, Type, Union

from colorama import Fore, Style
from tabulate import tabulate

from croud.typing import JsonDict


def print_format(
    rows: Union[List[JsonDict], JsonDict], format: str, keys: Optional[List[str]] = None
) -> None:
    try:
        Printer = PRINTERS[format]
    except KeyError:
        print_error("This print method is not supported.")
        exit(1)
    printer = Printer(keys)
    printer.print_rows(rows)


def print_error(text: str):
    print(Fore.RED + "==> Error: " + Style.RESET_ALL + text)


def print_info(text: str):
    print(Fore.CYAN + "==> Info: " + Style.RESET_ALL + text)


def print_success(text: str):
    print(Fore.GREEN + "==> Success: " + Style.RESET_ALL + text)


class FormatPrinter(abc.ABC):
    def __init__(self, keys: Optional[List[str]] = None):
        self.keys = keys

    def print_rows(self, rows: Union[List[JsonDict], JsonDict]) -> None:
        print(self.format_rows(rows))

    @abc.abstractmethod
    def format_rows(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        raise NotImplementedError()


class JsonFormatPrinter(FormatPrinter):
    def format_rows(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        return json.dumps(rows, sort_keys=False, indent=2)


class TableFormatPrinter(FormatPrinter):
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
            [self._transform_record_value(row[header]) for header in headers]
            for row in rows
        ]

        return tabulate(values, headers=headers, tablefmt="psql", missingval="NULL")

    def _filter_record(self, data: dict, keys: List[str]) -> JsonDict:
        return {key: value for key, value in data.items() if key in keys}

    def _transform_record_value(self, field):
        """transform field for displaying"""
        if isinstance(field, (list, dict)):
            return json.dumps(field, sort_keys=True, ensure_ascii=False)
        elif isinstance(field, bool):
            return "TRUE" if field else "FALSE"
        else:
            return field


PRINTERS: Dict[str, Union[Type[JsonFormatPrinter], Type[TableFormatPrinter]]] = {
    "json": JsonFormatPrinter,
    "table": TableFormatPrinter,
}
