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

from croud.config import (
    Configuration,
    IncompatibleConfigException,
    load_config,
    write_config,
)


class TestConfiguration(unittest.TestCase):
    @mock.patch.object(Configuration, "validate", return_value={})
    @mock.patch("yaml.load")
    def test_load_config(self, mock_yaml_load, mock_validate):
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            load_config()

        mock_yaml_load.assert_called_once_with(m())

    @mock.patch("yaml.dump")
    def test_write_config(self, mock_yaml_dump):
        config = {"env": "dev", "token": "eyJraWQiOiIxZTlnZGs3IiwiYWxnIjoiUlMyNTYifQ"}
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            write_config(config)

        mock_yaml_dump.assert_called_once_with(
            config, m(), default_flow_style=False, allow_unicode=True
        )

    def test_incompatible_schema(self):
        config = {"incompatible": "", "schema": ""}
        with self.assertRaises(IncompatibleConfigException) as cm:
            Configuration.validate(config)

        self.assertTrue("Incompatible storage format" in str(cm.exception))
