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
from tests.util import CommandTestCase, call_command


def gen_uuid() -> str:
    return str(uuid.uuid4())


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class TestConsumers(CommandTestCase):
    # fmt: off
    eventhub_dsn = "Endpoint=sb://myhub.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=..."  # noqa
    storage_dsn = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"  # noqa
    # fmt: on

    @mock.patch.object(Client, "send", return_value=["data", "errors"])
    def test_deploy_consumer(self, mock_send, mock_load_config):
        project_id = gen_uuid()
        cluster_id = gen_uuid()

        argv = [
            "croud",
            "consumers",
            "deploy",
            "--product-name",
            "eventhub-consumer",
            "--tier",
            "S0",
            "--num-instances",
            "2",
            "--project-id",
            project_id,
            "--cluster-id",
            cluster_id,
            "--consumer-name",
            "my-eventhub-consumer",
            "--consumer-table",
            "raw",
            "--consumer-schema",
            "doc",
            "--eventhub-dsn",
            self.eventhub_dsn,
            "--eventhub-consumer-group",
            "$Default",
            "--lease-storage-dsn",
            self.storage_dsn,
            "--lease-storage-container",
            "lease_container",
        ]

        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/consumers/",
            body={
                "cluster_id": cluster_id,
                "config": {
                    "connection_string": self.eventhub_dsn,
                    "consumer_group": "$Default",
                    "lease_storage_connection_string": self.storage_dsn,
                    "consumer_lease_container": "lease_container",
                },
                "instances": 2,
                "name": "my-eventhub-consumer",
                "product_name": "eventhub-consumer",
                "product_tier": "S0",
                "project_id": project_id,
                "table_name": "raw",
                "table_schema": "doc",
            },
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_consumers_list(self, mock_send, mock_load_config):
        argv = ["croud", "consumers", "list"]
        self.assertRest(
            mock_send, argv, RequestMethod.GET, "/api/v2/consumers/", params={}
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_consumers_list_with_params(self, mock_send, mock_load_config):
        project_id = gen_uuid()
        cluster_id = gen_uuid()
        argv = [
            "croud",
            "consumers",
            "list",
            "--project-id",
            project_id,
            "--cluster-id",
            cluster_id,
            "--product-name",
            "eventhub-consumer",
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.GET,
            "/api/v2/consumers/",
            params={
                "product_name": "eventhub-consumer",
                "project_id": project_id,
                "cluster_id": cluster_id,
            },
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_consumers_edit(self, mock_send, mock_load_config):
        consumer_id = gen_uuid()
        cluster_id = gen_uuid()

        argv = [
            "croud",
            "consumers",
            "edit",
            "--consumer-id",
            consumer_id,
            "--eventhub-dsn",
            self.eventhub_dsn,
            "--eventhub-consumer-group",
            "$Default",
            "--lease-storage-dsn",
            self.storage_dsn,
            "--lease-storage-container",
            "lease_container",
            "--consumer-schema",
            "doc",
            "--consumer-table",
            "raw",
            "--cluster-id",
            cluster_id,
        ]

        self.assertRest(
            mock_send,
            argv,
            RequestMethod.PATCH,
            f"/api/v2/consumers/{consumer_id}/",
            body={
                "cluster_id": cluster_id,
                "config": {
                    "connection_string": self.eventhub_dsn,
                    "consumer_group": "$Default",
                    "lease_storage_connection_string": self.storage_dsn,
                    "consumer_lease_container": "lease_container",
                },
                "table_name": "raw",
                "table_schema": "doc",
            },
        )

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_consumers_delete(self, mock_send, mock_load_config, capsys):
        consumer_id = gen_uuid()
        argv = ["croud", "consumers", "delete", "--consumer-id", consumer_id]
        with mock.patch("builtins.input", side_effect=["YES"]) as mock_input:
            self.assertRest(
                mock_send,
                argv,
                RequestMethod.DELETE,
                f"/api/v2/consumers/{consumer_id}/",
            )
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the consumer? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Consumer deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_consumers_delete_flag(self, mock_send, mock_load_config, capsys):
        consumer_id = gen_uuid()
        argv = ["croud", "consumers", "delete", "--consumer-id", consumer_id, "-y"]
        with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
            self.assertRest(
                mock_send,
                argv,
                RequestMethod.DELETE,
                f"/api/v2/consumers/{consumer_id}/",
            )
            mock_input.assert_not_called()

        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Consumer deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_consumers_delete_aborted(self, mock_send, mock_load_config, capsys):
        consumer_id = gen_uuid()
        argv = ["croud", "consumers", "delete", "--consumer-id", consumer_id]
        with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
            call_command(*argv)
            mock_send.assert_not_called()
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the consumer? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Consumer deletion cancelled." in err_output


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
