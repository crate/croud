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

from unittest import mock

from croud.config import Configuration
from croud.rest import Client
from croud.session import RequestMethod
from tests.util import assert_rest, call_command, gen_uuid


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_monitoring_grafana_enable(mock_send, mock_config):
    project_id = gen_uuid()
    call_command("croud", "monitoring", "grafana", "enable", "--project-id", project_id)
    assert_rest(
        mock_send,
        RequestMethod.POST,
        "/api/v2/monitoring/grafana/",
        body={"project_id": project_id},
    )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
def test_monitoring_grafana_disable(mock_send, mock_config):
    project_id = gen_uuid()
    call_command(
        "croud", "monitoring", "grafana", "disable", "--project-id", project_id
    )
    assert_rest(
        mock_send,
        RequestMethod.DELETE,
        "/api/v2/monitoring/grafana/",
        body={"project_id": project_id},
    )
