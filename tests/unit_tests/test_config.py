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

import os
import tempfile
import unittest
import uuid
from unittest import mock

from yaml.constructor import ConstructorError

from croud.config import Configuration, load_config, write_config


class TestConfiguration(unittest.TestCase):
    @mock.patch.object(Configuration, "validate", return_value={})
    @mock.patch("yaml.safe_load")
    def test_load_config(self, mock_yaml_load, mock_validate):
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            load_config()

        mock_yaml_load.assert_called_once_with(m())

    @mock.patch("yaml.dump")
    def test_write_config(self, mock_yaml_dump):
        config = Configuration.DEFAULT_CONFIG
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            write_config(config)

        mock_yaml_dump.assert_called_once_with(
            config, m(), default_flow_style=False, allow_unicode=True
        )

    @mock.patch("croud.config.os.remove")
    @mock.patch("croud.config.os.chmod")
    @mock.patch("croud.config.write_config")
    def test_incompatible_schema_rewrites_config(
        self, mock_write_config, mock_chmod, mock_remove
    ):
        config = {"incompatible": "", "schema": ""}

        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            Configuration.validate(config)
            self.assertTrue(mock_remove.called)

            mock_write_config.assert_called_once_with(Configuration.DEFAULT_CONFIG)

    def test_yaml_safe_load(self):
        new_file = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
        with tempfile.NamedTemporaryFile(mode="w+") as tmp:
            tmp.write(
                "insecure: !!python/object/apply:"
                f"subprocess.run [['touch', '{new_file}']]"
            )
            tmp.flush()
            self.assertFalse(os.path.exists(new_file))
            with mock.patch.object(Configuration, "FILEPATH", tmp.name):
                with self.assertRaisesRegex(
                    ConstructorError,
                    r"tag:yaml.org,\d+:python/object/apply:subprocess.run",
                ):
                    load_config()

            self.assertFalse(os.path.exists(new_file))
