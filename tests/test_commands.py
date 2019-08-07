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

import uuid
from unittest import mock

from croud.config import Configuration
from croud.rest import Client
from croud.session import RequestMethod
from tests.util import CommandTestCase


def gen_uuid() -> str:
    return str(uuid.uuid4())


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
class TestGrafana(CommandTestCase):
    project_id = gen_uuid()

    def test_enable(self, mock_send, mock_config):
        argv = [
            "croud",
            "monitoring",
            "grafana",
            "enable",
            "--project-id",
            self.project_id,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/monitoring/grafana/",
            body={"project_id": self.project_id},
        )

    def test_disable(self, mock_send, mock_config):
        argv = [
            "croud",
            "monitoring",
            "grafana",
            "disable",
            "--project-id",
            self.project_id,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.DELETE,
            "/api/v2/monitoring/grafana/",
            body={"project_id": self.project_id},
        )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class TestProducts(CommandTestCase):
    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list(self, mock_send, mock_load_config):
        argv = ["croud", "products", "list"]
        self.assertRest(mock_send, argv, RequestMethod.GET, "/api/v2/products/")

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list_kind(self, mock_send, mock_load_config):
        argv = ["croud", "products", "list", "--kind", "cluster"]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.GET,
            "/api/v2/products/",
            params={"kind": "cluster"},
        )
