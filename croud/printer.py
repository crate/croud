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

import json
from typing import List, Union

from colorama import Fore, Style
from tabulate import tabulate

from croud.typing import JsonDict


def print_format(rows: Union[List[JsonDict], JsonDict], format: str = "json") -> None:
    printer = FormatPrinter()
    printer.print_rows(rows, format)


def print_error(text: str):
    print(Fore.RED + "==> Error: " + Style.RESET_ALL + text)


def print_info(text: str):
    print(Fore.CYAN + "==> Info: " + Style.RESET_ALL + text)


def print_success(text: str):
    print(Fore.GREEN + "==> Success: " + Style.RESET_ALL + text)


class FormatPrinter:
    def __init__(self):
        self.supported_formats: dict = {"json": self._json, "table": self._tabular}

    def print_rows(self, rows: Union[List[JsonDict], JsonDict], format: str) -> None:
        try:
            print_method = self.supported_formats[format]
        except KeyError as e:
            print_error(f"This print method is not supported: {e!s}")
            exit(1)
        print(print_method(rows))

    def _transform_field(self, field):
        """transform field for displaying"""
        if isinstance(field, (list, dict)):
            return json.dumps(field, sort_keys=True, ensure_ascii=False)
        elif isinstance(field, bool):
            return "TRUE" if field else "FALSE"
        else:
            return field

    def _json(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        return json.dumps(rows, sort_keys=False, indent=2)

    def _tabular(self, rows: Union[List[JsonDict], JsonDict]) -> str:
        if isinstance(rows, list):
            # ensure that keys are mapped to their values
            # e.g. Rows, generated with
            # [{"a": "foo", "b": 1}, {"b": 2, "a": "bar"}]
            # should get printed same as
            # [{"a": "foo", "b": 1}, {"a": "bar", "b": "1"}]
            # +-----+-----+
            # | a   |   b |
            # |-----+-----+
            # | foo |   1 |
            # +-----+-----+
            # | bar |   2 |
            # +-----+-----+
            headers = list(map(str, iter(rows[0].keys())))
            values = [
                [self._transform_field(row[header]) for header in headers]
                for row in rows
            ]
        else:
            headers = list(map(str, iter(rows.keys())))
            values = [list(map(self._transform_field, rows.values()))]
        return tabulate(values, headers=headers, tablefmt="psql", missingval="NULL")
