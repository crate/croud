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

import asyncio
from argparse import Namespace
from unittest.mock import patch

import pytest

from croud.config import Configuration
from croud.gql import Query, print_query


@pytest.mark.parametrize(
    "input,expected", [(Namespace(env="dev"), "dev"), (Namespace(env=None), "prod")]
)
@patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
def test_env_set(mock_load_config, input, expected):
    query = Query("{}", input)
    assert query._env == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (Namespace(env="dev", output_fmt="json"), "json"),
        (Namespace(env="dev", output_fmt=None), "table"),
        (Namespace(env="dev"), "table"),
    ],
)
@patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
def test_output_fmt_set(mock_load_config, input, expected):
    query = Query("{}", input)
    assert query._output_fmt == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (Namespace(env="dev", region="westeurope.azure"), "westeurope.azure"),
        (Namespace(env="dev", region=None), "bregenz.a1"),
        (Namespace(env="dev"), "bregenz.a1"),
    ],
)
@patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
def test_region_set(mock_load_config, input, expected):
    query = Query("{}", input)
    assert query._region == expected


@patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class PrintQueryTest:
    @patch("croud.gql.print_error")
    def test_print_query_error(self, print_error, load_config):
        query = Query("", Namespace(env="test"))
        query._error = "This is a GraphQL error message"

        print_query(query)
        print_error.assert_called_once_with(query._error)

    @patch("croud.gql.print_info")
    def test_print_query_no_response(self, print_info, load_config):
        query = Query("", Namespace(env="test"))
        query._response = {}

        print_query(query)
        expected_message = "Result contained no data to print."
        print_info.assert_called_once_with(expected_message)

    @patch("croud.gql.print_error")
    def test_print_query_malformatted_response(self, print_error, load_config):
        query = Query("", Namespace(env="test"))
        query._response = 42

        print_query(query)
        expected_message = "Result has no proper format to print."
        print_error.assert_called_once_with(expected_message)

    @pytest.mark.parametrize("format", ["json", "tabular"])
    @pytest.mark.parametrize(
        "response, key",
        [
            ({"data": ["foo", "bar"]}, None),
            ({"allNames": {"data": ["foo", "bar"]}}, "allNames"),
            ({"allNames": ["foo", "bar"]}, "allNames"),
        ],
    )
    @patch("croud.gql.print_format")
    def test_print_query_data(self, print_format, response, key, format, load_config):
        query = Query("", Namespace(env="test", output_fmt=format))
        query._response = response

        print_query(query, key)
        print_format.assert_called_once_with(["foo", "bar"], format)

    @pytest.mark.parametrize(
        "response, key",
        [
            ({"data": []}, None),
            ({"allNames": {"data": []}}, "allNames"),
            ({"allNames": []}, "allNames"),
        ],
    )
    @patch("croud.gql.print_info")
    def test_print_query_no_data(self, print_info, response, key, load_config):
        query = Query("", Namespace(env="test"))
        query._response = response

        print_query(query, key)
        expected_message = "Result contained no data to print."
        print_info.assert_called_once_with(expected_message)


@patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
def test_execute_query_with_variables(load_config):
    query = Query("", Namespace(env="test"))
    vars = {"a": "foo", "b": 42}

    result_future = asyncio.Future()
    result_future.set_result({"data": []})
    with patch.object(query, "_fetch_data", return_value=result_future) as fetch_data:
        query.execute(vars)

    fetch_data.assert_called_once_with(vars)
