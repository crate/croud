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

import textwrap
import uuid
from argparse import Namespace
from unittest import mock

import pytest
from util import CommandTestCase

from croud.config import Configuration, config_get, config_set
from croud.gql import Query
from croud.rest import Client
from croud.session import RequestMethod


def gen_uuid() -> str:
    return str(uuid.uuid4())


class TestConfigGet:
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_get_env(self, mock_print, mock_load_config):
        config_get(Namespace(get="env"))
        mock_print.assert_called_once_with("prod")

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_get_top_level_setting(self, mock_print, mock_load_config):
        config_get(Namespace(get="region"))
        mock_print.assert_called_once_with("bregenz.a1")


class TestConfigSet:
    @mock.patch("croud.config.write_config")
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_set_env(self, mock_load_config, mock_write_config):
        config = Configuration.DEFAULT_CONFIG
        config["auth"]["current_context"] = "prod"

        config_set(Namespace(env="prod"))
        mock_write_config.assert_called_once_with(config)

    @mock.patch("croud.config.write_config")
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_set_top_level_setting(self, mock_load_config, mock_write_config):
        config = Configuration.DEFAULT_CONFIG
        config["region"] = "eastus.azure"

        config_set(Namespace(region="eastus.azure"))
        mock_write_config.assert_called_once_with(config)

        config["region"] = "bregenz.a1"


def assert_query(mock_print, expected):
    actual = mock_print.call_args[0][0]._query
    assert actual == expected


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestClusters(CommandTestCase):
    project_id = gen_uuid()
    expected_body = textwrap.dedent(
        """
        query allClusters($filter: [ClusterFilter]) {
            allClusters(sort: [CRATE_VERSION_DESC], filter: $filter) {
                data {
                    id
                    name
                    numNodes
                    crateVersion
                    projectId
                    username
                    fqdn
                }
            }
        }
    """
    ).strip()

    def test_list_no_project_id(self, mock_run, mock_load_config):
        argv = ["croud", "clusters", "list"]
        expected_vars = {}
        self.assertGql(mock_run, argv, self.expected_body, expected_vars)

    def test_list_with_project_id(self, mock_run, mock_load_config):
        argv = ["croud", "clusters", "list", "--project-id", self.project_id]
        expected_vars = {
            "filter": [{"by": "PROJECT_ID", "op": "EQ", "value": self.project_id}]
        }
        self.assertGql(mock_run, argv, self.expected_body, expected_vars)

    def test_crate_clusters(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
            mutation deployCluster($input: DeployClusterInput!) {
                deployCluster(input: $input) {
                    id
                    name
                    fqdn
                    url
                }
            }
        """  # noqa
        ).strip()

        project_id = gen_uuid()

        expected_vars = {
            "input": {
                "productName": "crate-default",
                "tier": "S0",
                "unit": 1,
                "name": "crate_cluster",
                "projectId": project_id,
                "username": "foobar",
                "password": "s3cr3t!",
                "version": "3.2.5",
            }
        }

        argv = [
            "croud",
            "clusters",
            "deploy",
            "--product-name",
            "crate-default",
            "--tier",
            "S0",
            "--unit",
            "1",
            "--project-id",
            project_id,
            "--cluster-name",
            "crate_cluster",
            "--version",
            "3.2.5",
            "--username",
            "foobar",
            "--password",
            "s3cr3t!",
        ]

        self.assertGql(mock_run, argv, expected_body, expected_vars)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestOrganizations(CommandTestCase):
    def test_create(self, mock_run, mock_load_config):
        expected_body = """
    mutation {
        createOrganization(input: {
            name: "testorg",
            planType: 1
        }) {
            id
            name
            planType
        }
    }
    """

        argv = [
            "croud",
            "organizations",
            "create",
            "--name",
            "testorg",
            "--plan-type",
            "1",
        ]
        self.assertGql(mock_run, argv, expected_body)

    def test_list(self, mock_run, mock_load_config):
        expected_body = """
    {
        allOrganizations {
            data {
                id,
                name,
                planType,
                notification {
                    alert {
                        email,
                        enabled
                    }
                }
            }
        }
    }
    """

        argv = ["croud", "organizations", "list"]
        self.assertGql(mock_run, argv, expected_body)

    def test_add_user(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
            mutation addUserToOrganization($input: AddUserToOrganizationInput!) {
              addUserToOrganization(input: $input) {
                user {
                  uid
                  email
                  organizationId
                }
              }
            }
        """
        ).strip()
        expected_vars = {"input": {"user": "test@crate.io", "organizationId": None}}

        argv = ["croud", "organizations", "users", "add", "--user", "test@crate.io"]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_add_user_fqn(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
            mutation addUserToOrganization($input: AddUserToOrganizationInput!) {
              addUserToOrganization(input: $input) {
                user {
                  uid
                  email
                  organizationId
                }
              }
            }
        """
        ).strip()
        expected_vars = {
            "input": {
                "roleFqn": "org_admin",
                "user": "test@crate.io",
                "organizationId": None,
            }
        }

        argv = [
            "croud",
            "organizations",
            "users",
            "add",
            "--user",
            "test@crate.io",
            "--role",
            "org_admin",
        ]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_add_user_org_id(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
            mutation addUserToOrganization($input: AddUserToOrganizationInput!) {
              addUserToOrganization(input: $input) {
                user {
                  uid
                  email
                  organizationId
                }
              }
            }
        """
        ).strip()
        org_id = str(uuid.uuid4())
        expected_vars = {"input": {"organizationId": org_id, "user": "test@crate.io"}}

        argv = [
            "croud",
            "organizations",
            "users",
            "add",
            "--user",
            "test@crate.io",
            "--org-id",
            org_id,
        ]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_remove_user(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
            mutation removeUserFromOrganization($input: RemoveUserFromOrganizationInput!) {
              removeUserFromOrganization(input: $input) {
                success
              }
            }
        """  # noqa
        ).strip()

        user_id = str(uuid.uuid4())
        expected_vars = {"input": {"user": user_id, "organizationId": None}}

        argv = ["croud", "organizations", "users", "remove", "--user", user_id]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_remove_user_org_id(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
            mutation removeUserFromOrganization($input: RemoveUserFromOrganizationInput!) {
              removeUserFromOrganization(input: $input) {
                success
              }
            }
        """  # noqa
        ).strip()

        user_id = str(uuid.uuid4())
        org_id = str(uuid.uuid4())
        expected_vars = {"input": {"user": user_id, "organizationId": org_id}}

        argv = [
            "croud",
            "organizations",
            "users",
            "remove",
            "--user",
            user_id,
            "--org-id",
            org_id,
        ]
        self.assertGql(mock_run, argv, expected_body, expected_vars)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestProjects(CommandTestCase):
    def test_create(self, mock_run, mock_load_config):
        expected_body = """
    mutation {
        createProject(input: {
            name: "new-project",
            organizationId: "organization-id"
        }) {
            id
        }
    }
    """

        argv = [
            "croud",
            "projects",
            "create",
            "--name",
            "new-project",
            "--org-id",
            "organization-id",
        ]
        self.assertGql(mock_run, argv, expected_body)

    def test_list_projects_org_admin(self, mock_run, mock_load_config):
        expected_body = """
    {
        allProjects {
            data {
                id
                name
                region
                organizationId
            }
        }
    }
    """

        argv = ["croud", "projects", "list"]
        self.assertGql(mock_run, argv, expected_body)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestProjectsUsers(CommandTestCase):
    def test_add(self, mock_run, mock_load_config):
        expected_body = """
    mutation {
        addUserToProject(input: {
            projectId: "project-id",
            user: "user-email-or-id"
        }) {
            success
        }
    }
    """

        argv = [
            "croud",
            "projects",
            "users",
            "add",
            "--project-id",
            "project-id",
            "--user",
            "user-email-or-id",
        ]
        self.assertGql(mock_run, argv, expected_body)

    def test_remove(self, mock_run, mock_load_config):
        expected_body = """
    mutation {
        removeUserFromProject(input: {
            projectId: "project-id",
            user: "user-email-or-id"
        }) {
            success
        }
    }
    """

        argv = [
            "croud",
            "projects",
            "users",
            "remove",
            "--project-id",
            "project-id",
            "--user",
            "user-email-or-id",
        ]
        self.assertGql(mock_run, argv, expected_body)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestUsersRoles(CommandTestCase):
    def test_add(self, mock_run, mock_load_config):
        user_id = gen_uuid()
        role_fqn = "org_admin"
        resource_id = gen_uuid()

        expected_body = textwrap.dedent(
            """
            mutation addRoleToUser($input: UserRoleInput!) {
                addRoleToUser(input: $input) {
                    success
                }
            }
        """
        ).strip()
        expected_vars = {
            "input": {"userId": user_id, "roleFqn": role_fqn, "resourceId": resource_id}
        }

        argv = [
            "croud",
            "users",
            "roles",
            "add",
            "--user",
            user_id,
            "--role",
            role_fqn,
            "--resource",
            resource_id,
        ]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_remove(self, mock_run, mock_load_config):
        user_id = gen_uuid()
        role_fqn = "org_admin"
        resource_id = gen_uuid()

        expected_body = textwrap.dedent(
            """
            mutation removeRoleFromUser($input: UserRoleInput!) {
                removeRoleFromUser(input: $input) {
                    success
                }
            }
        """
        ).strip()
        expected_vars = {
            "input": {"userId": user_id, "roleFqn": role_fqn, "resourceId": resource_id}
        }

        argv = [
            "croud",
            "users",
            "roles",
            "remove",
            "--user",
            user_id,
            "--role",
            role_fqn,
            "--resource",
            resource_id,
        ]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_list(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
        query {
            allRoles {
                data {
                    fqn
                    friendlyName
                }
            }
        }
    """
        ).strip()

        argv = ["croud", "users", "roles", "list"]
        self.assertGql(mock_run, argv, expected_body)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestUsers(CommandTestCase):
    org_id = gen_uuid()
    expected_body = textwrap.dedent(
        """
        query allUsers($queryArgs: UserQueryArgs) {
            allUsers(sort: EMAIL, queryArgs: $queryArgs) {
                data {
                    uid
                    email
                    username
                }
            }
        }
    """
    ).strip()

    def test_list_no_filter(self, mock_run, mock_load_config):
        expected_vars = {"queryArgs": {"noOrg": False}}
        argv = ["croud", "users", "list"]
        self.assertGql(mock_run, argv, self.expected_body, expected_vars)

    def test_list_org_filter(self, mock_run, mock_load_config):
        expected_vars = {"queryArgs": {"organizationId": self.org_id, "noOrg": False}}
        argv = ["croud", "users", "list", "--org-id", self.org_id]
        self.assertGql(mock_run, argv, self.expected_body, expected_vars)

    def test_list_no_org_filter(self, mock_run, mock_load_config):
        expected_vars = {"queryArgs": {"noOrg": True}}
        argv = ["croud", "users", "list", "--no-org"]
        self.assertGql(mock_run, argv, self.expected_body, expected_vars)

    def test_list_filter_conflict(self, mock_run, mock_load_config):
        expected_vars = None
        argv = ["croud", "users", "list", "--org-id", self.org_id, "--no-org"]
        with mock.patch("sys.stderr.write") as stderr:
            with pytest.raises(SystemExit) as ex_info:
                self.assertGql(mock_run, argv, self.expected_body, expected_vars)
            stderr.assert_called_once()
            expected_error = "Argument --no-org: not allowed with argument --org-id\n\n"
            assert stderr.call_args[0][0] == expected_error
            assert ex_info.value.code == 2


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestConsumers(CommandTestCase):
    # fmt: off
    eventhub_dsn = "Endpoint=sb://myhub.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=..."  # noqa
    storage_dsn = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"  # noqa
    # fmt: on

    def test_deploy_consumer(self, mock_run, mock_load_config):
        project_id = gen_uuid()
        cluster_id = gen_uuid()

        expected_body = textwrap.dedent(
            """
        mutation deployConsumer($input: DeployConsumerInput!) {
            deployConsumer(input: $input) {
                id
                name
                projectId
                clusterId
                productName
                productTier
                instances
                tableName
                tableSchema
            }
        }
        """  # noqa
        ).strip()

        expected_vars = {
            "input": {
                "clusterId": cluster_id,
                "eventhubConnectionString": self.eventhub_dsn,
                "eventhubConsumerGroup": "$Default",
                "instances": 2,
                "leaseStorageConnectionString": self.storage_dsn,
                "leaseStorageContainer": "lease_container",
                "name": "my-eventhub-consumer",
                "productName": "eventhub-consumer",
                "productTier": "S0",
                "projectId": project_id,
                "tableName": "raw",
                "tableSchema": "doc",
            }
        }

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

        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_consumers_list(self, mock_run, mock_load_config):

        expected_body = textwrap.dedent(
            """
    query allConsumers($clusterId: ID, $productName: String, $projectId: ID) {
        allConsumers(clusterId: $clusterId, productName: $productName, projectId: $projectId) {
            id
            name
            projectId
            clusterId
            productName
            productTier
            instances
            tableName
            tableSchema
        }
    }
    """  # noqa
        ).strip()

        project_id = gen_uuid()
        cluster_id = gen_uuid()

        expected_vars = {
            "productName": "eventhub-consumer",
            "projectId": project_id,
            "clusterId": cluster_id,
        }

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

        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_consumers_edit(self, mock_run, mock_load_config):
        expected_body = textwrap.dedent(
            """
    mutation editConsumer($id: String!, $input: EditConsumerInput!) {
        editConsumer(id: $id, input: $input) {
            id
        }
    }
    """  # noqa
        ).strip()

        consumer_id = gen_uuid()
        cluster_id = gen_uuid()

        expected_vars = {
            "id": consumer_id,
            "input": {
                "eventhubConnectionString": self.eventhub_dsn,
                "eventhubConsumerGroup": "$Default",
                "leaseStorageConnectionString": self.storage_dsn,
                "leaseStorageContainer": "lease_container",
                "consumerSchema": "doc",
                "consumerTable": "raw",
                "clusterId": cluster_id,
            },
        }

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

        self.assertGql(mock_run, argv, expected_body, expected_vars)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send")
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
            {"project_id": self.project_id},
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
            {"project_id": self.project_id},
        )
