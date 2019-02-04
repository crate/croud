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

import unittest
from argparse import Namespace
from unittest import mock

from croud.config import Configuration
from croud.exceptions import GQLError
from croud.gql import Query


class TestHttpSession(unittest.TestCase):
    _data = {"data": {"key": "value"}}
    _error_data = {"errors": [{"message": "error"}]}

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_env_set(self, mock_load_config):
        args = Namespace(env="dev")
        query = Query("{}", args)

        self.assertEqual("dev", query._env)

        args = Namespace(env=None)
        query = Query("{}", args)

        self.assertEqual("prod", query._env)

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_output_fmt_set(self, mock_load_config):
        args = Namespace(env="dev", output_fmt="json")
        query = Query("{}", args)

        self.assertEqual("json", query._output_fmt)

        args = Namespace(env="dev", output_fmt=None)
        query = Query("{}", args)

        self.assertEqual("table", query._output_fmt)

        args = Namespace(env="dev")
        query = Query("{}", args)

        self.assertEqual("table", query._output_fmt)

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_region_set(self, mock_load_config):
        args = Namespace(env="dev", region="westeurope.azure")
        query = Query("{}", args)

        self.assertEqual("westeurope.azure", query._region)

        args = Namespace(env="dev", region=None)
        query = Query("{}", args)

        self.assertEqual("bregenz.a1", query._region)

        args = Namespace(env="dev")
        query = Query("{}", args)

        self.assertEqual("bregenz.a1", query._region)

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch.object(Query, "run", return_value=_data)
    def test_get_rows(self, mock_run, mock_load_config):
        query = Query("{}", Namespace(env="dev"))
        data = query._get_rows()

        self.assertEqual(self._data["data"], data)

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch.object(Query, "run", return_value=_error_data)
    def test_get_rows_error(self, mock_run, mock_load_config):
        query = Query("{}", Namespace(env="dev"))

        with self.assertRaises(GQLError):
            query._get_rows()

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch.object(Query, "_get_rows", return_value=_data["data"])
    def test_check_rows(self, mock_get_rows, mock_load_config):
        query = Query("{}", Namespace(env="dev"))
        data = query._get_rows()

        self.assertEqual(True, query._check_rows(data))

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("croud.gql.print_info")
    @mock.patch.object(Query, "_get_rows", return_value=[])
    def test_check_rows_empty(self, mock_get_rows, mock_print_info, mock_load_config):
        query = Query("{}", Namespace(env="dev"))
        data = query._get_rows()

        rows_ok = query._check_rows(data)
        self.assertEqual(False, rows_ok)

        mock_print_info.assert_called_once_with("Result contained no data to print.")

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("croud.gql.print_error")
    @mock.patch.object(Query, "_get_rows", return_value="string")
    def test_check_rows_bad_format(
        self, mock_get_rows, mock_print_error, mock_load_config
    ):
        query = Query("{}", Namespace(env="dev"))
        data = query._get_rows()

        rows_ok = query._check_rows(data)
        self.assertEqual(False, rows_ok)

        message = "Result has no proper format to print."
        mock_print_error.assert_called_once_with(message)

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("croud.gql.print_format")
    @mock.patch.object(Query, "_get_rows", return_value=_data["data"])
    def test_print_result(self, mock_get_rows, mock_print_format, mock_load_config):
        query = Query("{}", Namespace(env="dev"))
        query.print_result("key")

        mock_print_format.assert_called_once_with(self._data["data"]["key"], "table")

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("croud.gql.print_error")
    @mock.patch.object(Query, "run", return_value=_error_data)
    def test_print_result_error(self, mock_run, mock_print_error, mock_load_config):
        query = Query("{}", Namespace(env="dev"))
        query.print_result("key")

        message = self._error_data["errors"][0]["message"]
        mock_print_error.assert_called_once_with(message)

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("croud.gql.print_info")
    @mock.patch.object(Query, "run", return_value={"data": []})
    def test_print_result_empty(self, mock_get_rows, mock_print_info, mock_load_config):
        query = Query("{}", Namespace(env="dev"))
        query.print_result("key")

        mock_print_info.assert_called_once_with("Result contained no data to print.")
