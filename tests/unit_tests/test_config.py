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
from unittest import mock

from croud.config import Configuration


class TestConfiguration(unittest.TestCase):
    def test_write_token(self):
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            Configuration.write_token("eyJraWQiOiIxZTlnZGs3IiwiYWxnIjoiUlMyNTYifQ")

        m.assert_called_once_with(Configuration.CONFIG_PATH, "w")
        handle = m()
        handle.write.assert_called_once_with(
            "eyJraWQiOiIxZTlnZGs3IiwiYWxnIjoiUlMyNTYifQ"
        )

    @mock.patch("pathlib.Path.exists", return_value=True)
    def test_read_token_exists(self, mock_path_exists):
        m = mock.mock_open(read_data="eyJraWQiOiIxZTlnZGs3IiwiYWxnIjoiUlMyNTYifQ")
        with mock.patch("croud.config.open", m, create=True):
            token = Configuration.read_token()

        m.assert_called_once_with(Configuration.CONFIG_PATH)
        self.assertEqual(token, "eyJraWQiOiIxZTlnZGs3IiwiYWxnIjoiUlMyNTYifQ")

    @mock.patch("pathlib.Path.exists", return_value=False)
    def test_read_token_not_exists(self, mock_path_exists):
        token = Configuration.read_token()
        self.assertEqual(token, "")
