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

from croud.printer import (
    JsonFormatPrinter,
    TableFormatPrinter,
    WideTableFormatPrinter,
    YamlFormatPrinter,
    print_response,
)


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
    "rows,expected",
    (
        (None, "null\n...\n"),
        ({}, "{}\n"),
        (
            {"a": "foo : bar", "b": 1, "c": True, "d": {"x": 1, "y": None, "z": False}},
            (
                "a: 'foo : bar'\n"
                "b: 1\n"
                "c: true\n"
                "d:\n"
                "  x: 1\n"
                "  y: null\n"
                "  z: false\n"
            ),
        ),
    ),
)
def test_yaml_format(rows, expected):
    out = YamlFormatPrinter().format_rows(rows)
    assert out == expected


@pytest.mark.parametrize(
    "rows,keys,transforms,expected",
    (
        (None, ["what", "ever"], None, ""),
        ({}, ["what", "ever"], None, ""),
        ([], [], None, ""),
        (
            [],
            ["what", "ever"],
            None,
            (
                "+--------+--------+\n"
                "| what   | ever   |\n"
                "|--------+--------|\n"
                "+--------+--------+"
            ),
        ),
        (
            {"a": "foo", "b": 1.234, "c": True, "d": "bar"},
            ["a", "b", "c"],
            {"a": str.upper, "b": int},
            (
                "+-----+-----+------+\n"
                "| a   |   b | c    |\n"
                "|-----+-----+------|\n"
                "| FOO |   1 | TRUE |\n"
                "+-----+-----+------+"
            ),
        ),
        (
            [
                {"a": "foo", "b": 1, "c": True},
                {"b": 2, "c": False, "a": {"bar": [{"value": 0}, {"value": 1}]}},
            ],
            None,
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
            [{"a": {"bar": "X"}, "b": [1, 2, 3]}, {"b": [2, 4, 8], "a": {"foo": "Y"}}],
            ["b", "a"],
            {"a": lambda field: field.get("bar", "N/A"), "b": sum},
            (
                "+-----+-----+\n"
                "|   b | a   |\n"
                "|-----+-----|\n"
                "|   6 | X   |\n"
                "|  14 | N/A |\n"
                "+-----+-----+"
            ),
        ),
        (
            {"k1": "v1", "k2": "v2", "k3": "v3"},
            ["k1", "k3"],
            None,
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
            None,
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
            None,
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
def test_tabular_format(rows, keys, transforms, expected):
    out = TableFormatPrinter(keys=keys, transforms=transforms).format_rows(rows)
    assert out == expected


@pytest.mark.parametrize(
    "rows,keys,transforms,expected",
    (
        (None, ["what", "ever"], None, ""),
        ({}, ["what", "ever"], None, ""),
        ([], [], None, ""),
        (
            [],
            ["what", "ever"],
            None,
            (
                "+--------+--------+\n"
                "| what   | ever   |\n"
                "|--------+--------|\n"
                "+--------+--------+"
            ),
        ),
        (
            {"a": "foo", "b": 1.234, "c": True, "d": "bar"},
            ["a", "b", "c"],
            {"a": str.upper, "b": int},
            (
                "+-----+-----+------+-----+\n"
                "| a   |   b | c    | d   |\n"
                "|-----+-----+------+-----|\n"
                "| FOO |   1 | TRUE | bar |\n"
                "+-----+-----+------+-----+"
            ),
        ),
    ),
)
def test_wide_format(rows, keys, transforms, expected):
    out = WideTableFormatPrinter(keys=keys, transforms=transforms).format_rows(rows)
    assert out == expected


def test_print_response(capsys):
    data = {"email": "test@crate.io", "username": "Google_1234"}
    errors = None
    output_fmt = "json"
    print_response(data, errors, output_fmt)
    output, _ = capsys.readouterr()
    assert "test@crate.io" in output
    assert "Google_1234" in output


def test_print_response_success_message(capsys):
    data = None
    errors = {}
    output_fmt = "json"
    success_message = "Deleted cluster."
    print_response(data, errors, output_fmt, success_message)
    _, err_output = capsys.readouterr()
    assert "Success" in err_output
    assert "Deleted cluster." in err_output


def test_print_response_error(capsys):
    data = None
    errors = {"message": "Resource not found.", "success": False}
    output_fmt = "table"
    print_response(data, errors, output_fmt)
    _, err_output = capsys.readouterr()
    assert "Error" in err_output
    assert "Resource not found." in err_output


def test_print_response_data_success(capsys):
    data = {"a": 1, "b": 2}
    errors = {}
    output_fmt = "json"
    success_message = "Posted numbers."
    print_response(data, errors, output_fmt, success_message)
    output, err_output = capsys.readouterr()
    assert '"a": 1' in output
    assert '"b": 2' in output
    assert "Success" in err_output
    assert "Posted numbers." in err_output
