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

import pytest

from croud.printer import JsonFormatPrinter, TableFormatPrinter


@pytest.mark.parametrize(
    "rows,expected",
    (
        (None, "null"),
        ({}, "{}"),
        (
            {"a": "foo", "b": 1, "c": True, "d": {"x": 1, "y": "xyz", "z": False}},
            (
                "{\n"
                '  "a": "foo",\n'
                '  "b": 1,\n'
                '  "c": true,\n'
                '  "d": {\n'
                '    "x": 1,\n'
                '    "y": "xyz",\n'
                '    "z": false\n'
                "  }\n"
                "}"
            ),
        ),
    ),
)
def test_json_format(rows, expected):
    out = JsonFormatPrinter().format_rows(rows)
    assert out == expected


@pytest.mark.parametrize(
    "rows,keys,expected",
    (
        (None, ["what", "ever"], ""),
        ({}, ["what", "ever"], ""),
        ([], [], ""),
        (
            [],
            ["what", "ever"],
            (
                "+--------+--------+\n"
                "| what   | ever   |\n"
                "|--------+--------|\n"
                "+--------+--------+"
            ),
        ),
        (
            {"a": "foo", "b": 1, "c": True},
            None,
            (
                "+-----+-----+------+\n"
                "| a   |   b | c    |\n"
                "|-----+-----+------|\n"
                "| foo |   1 | TRUE |\n"
                "+-----+-----+------+"
            ),
        ),
        (
            [
                {"a": "foo", "b": 1, "c": True},
                {"b": 2, "c": False, "a": {"bar": [{"value": 0}, {"value": 1}]}},
            ],
            None,
            (
                "+---------------------------------------+-----+-------+\n"
                "| a                                     |   b | c     |\n"
                "|---------------------------------------+-----+-------|\n"
                "| foo                                   |   1 | TRUE  |\n"
                '| {"bar": [{"value": 0}, {"value": 1}]} |   2 | FALSE |\n'
                "+---------------------------------------+-----+-------+"
            ),
        ),
        (
            {"k1": "v1", "k2": "v2", "k3": "v3"},
            ["k1", "k3"],
            (
                "+------+------+\n"
                "| k1   | k3   |\n"
                "|------+------|\n"
                "| v1   | v3   |\n"
                "+------+------+"
            ),
        ),
        (
            [
                {"k1": "v01", "k2": "v02", "k3": "v03"},
                {"k1": "v11", "k2": "v12", "k3": "v13"},
            ],
            ["k1", "k2"],
            (
                "+------+------+\n"
                "| k1   | k2   |\n"
                "|------+------|\n"
                "| v01  | v02  |\n"
                "| v11  | v12  |\n"
                "+------+------+"
            ),
        ),
        (
            [
                {"k1": "v01", "k2": "v02", "k3": "v03"},
                {"k1": "v11", "k2": "v12", "k3": "v13"},
            ],
            ["k1", "k2", "k4"],
            (
                "+------+------+\n"
                "| k1   | k2   |\n"
                "|------+------|\n"
                "| v01  | v02  |\n"
                "| v11  | v12  |\n"
                "+------+------+"
            ),
        ),
    ),
)
def test_tabular_format(rows, keys, expected):
    out = TableFormatPrinter(keys=keys).format_rows(rows)
    assert out == expected
