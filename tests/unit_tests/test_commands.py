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
from argparse import Namespace
from textwrap import dedent
from unittest import mock

import pytest
from util import CommandTestCase

from croud.clusters.commands import clusters_list
from croud.config import Configuration, config_get, config_set
from croud.gql import Query
from croud.login import _login_url, _set_login_env, login
from croud.logout import logout
from croud.organizations.commands import organizations_create, organizations_list
from croud.products.deploy import product_deploy
from croud.projects.commands import project_create, projects_list
from croud.projects.users.commands import project_user_add, project_user_remove
from croud.server import Server
from croud.users.commands import users_list
from croud.users.roles.commands import roles_add, roles_list, roles_remove


def gen_uuid() -> str:
    return str(uuid.uuid4())


class TestLogin:
    @mock.patch("croud.config.Configuration.set_context")
    @mock.patch("croud.config.Configuration.override_context")
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch.object(Server, "stop")
    @mock.patch.object(Server, "start")
    @mock.patch("croud.login.asyncio.get_event_loop")
    @mock.patch("croud.login.can_launch_browser", return_value=True)
    @mock.patch("croud.login.open_page_in_browser")
    @mock.patch("croud.login.print_info")
    def test_login_success(
        self,
        mock_print_info,
        mock_open_page_in_browser,
        mock_can_launch_browser,
        mock_loop,
        mock_start,
        mock_stop,
        mock_load_config,
        mock_override_context,
        mock_set_context,
    ):
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            login(Namespace(env=None))

        calls = [
            mock.call("A browser tab has been launched for you to login."),
            mock.call("Login successful."),
        ]
        mock_print_info.assert_has_calls(calls)

    @mock.patch("croud.config.Configuration.get_env", return_value="dev")
    @mock.patch("croud.login.can_launch_browser", return_value=False)
    @mock.patch("croud.login.print_error")
    def test_login_no_valid_browser(
        self, mock_print_error, mock_can_launch_browser, mock_get_env
    ):
        with pytest.raises(SystemExit) as e_info:
            login(Namespace(env=None))

        mock_print_error.assert_called_once_with(
            "Login only works with a valid browser installed."
        )
        assert e_info.value.code == 1

    @mock.patch("croud.config.Configuration.override_context")
    @mock.patch("croud.config.Configuration.get_env", return_value="dev")
    def test_login_env_from_current_context(self, mock_get_env, mock_override_context):
        env = _set_login_env(None)
        assert env == "dev"

    def test_login_env_override_context_from_argument(self):
        env = _set_login_env("prod")
        assert env == "prod"

    def test_login_urls_from_valid_envs(self):
        url = _login_url("dev")
        assert "https://bregenz.a1.cratedb-dev.cloud/oauth2/login?cli=true" == url

        url = _login_url("prod")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true" == url

        url = _login_url("PROD")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true" == url

    def test_env_fallback_url(self):
        url = _login_url("invalid")
        assert "https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true" == url


class TestLogout:
    @mock.patch("croud.config.Configuration.override_context")
    @mock.patch("croud.logout.Configuration.set_token")
    @mock.patch("croud.logout.print_info")
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_logout(
        self, mock_load_config, mock_print_info, mock_set_token, mock_override_context
    ):
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            logout(Namespace(env="dev"))

        mock_set_token.assert_called_once_with("")
        mock_print_info.assert_called_once_with("You have been logged out.")


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
class TestClusters:
    def test_list_no_pid(self, mock_execute, mock_load_config):
        query = """
{
    allClusters {
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

        args = Namespace(
            env=None, output_fmt="table", project_id=None, region="bregenz.a1"
        )
        with mock.patch("croud.clusters.commands.print_query") as mock_print:
            clusters_list(args)
            assert_query(mock_print, query)

    def test_list_with_pid(self, mock_execute, mock_load_config):
        query = (
            """
{
    allClusters (filter: %s) {
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
            % '{by: PROJECT_ID, op: EQ, value: "60d398b4-455b-49dc-bfe9-04edf5bd3eb2"}'
        )

        args = Namespace(
            env=None,
            output_fmt="table",
            project_id="60d398b4-455b-49dc-bfe9-04edf5bd3eb2",
            region="bregenz.a1",
        )
        with mock.patch("croud.clusters.commands.print_query") as mock_print:
            clusters_list(args)
            assert_query(mock_print, query)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestOrganizations(CommandTestCase):
    remove_input = "RemoveUserFromOrganizationInput"

    def test_create(self, mock_execute, mock_load_config):
        mutation = """
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

        args = Namespace(env="dev", name="testorg", output_fmt="json", plan_type=1)
        with mock.patch("croud.organizations.commands.print_query") as mock_print:
            organizations_create(args)
            assert_query(mock_print, mutation)

    def test_list(self, mock_execute, mock_load_config):
        query = """
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

        args = Namespace(env="dev")
        with mock.patch("croud.organizations.commands.print_query") as mock_print:
            organizations_list(args)
            assert_query(mock_print, query)

    def test_add_user(self, mock_run, mock_load_config):
        expected_body = dedent(
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
        expected_body = dedent(
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
        expected_body = dedent(
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
        expected_body = dedent(
            f"""
            mutation removeUserFromOrganization($input: {self.remove_input}!) {{
              removeUserFromOrganization(input: $input) {{
                success
              }}
            }}
        """
        ).strip()

        user_id = str(uuid.uuid4())
        expected_vars = {"input": {"uid": user_id, "organizationId": None}}

        argv = ["croud", "organizations", "users", "remove", "--user", user_id]
        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_remove_user_org_id(self, mock_run, mock_load_config):
        expected_body = dedent(
            f"""
            mutation removeUserFromOrganization($input: {self.remove_input}!) {{
              removeUserFromOrganization(input: $input) {{
                success
              }}
            }}
        """
        ).strip()

        user_id = str(uuid.uuid4())
        org_id = str(uuid.uuid4())
        expected_vars = {"input": {"uid": user_id, "organizationId": org_id}}

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
@mock.patch.object(Query, "execute")
class TestProjects:
    def test_create(self, mock_execute, mock_load_config):
        mutation = """
    mutation {
        createProject(input: {
            name: "new-project",
            organizationId: "organization-id"
        }) {
            id
        }
    }
    """

        args = Namespace(
            env="dev", name="new-project", org_id="organization-id", output_fmt="json"
        )
        with mock.patch("croud.projects.commands.print_query") as mock_print:
            project_create(args)
            assert_query(mock_print, mutation)

    def test_list_projects_org_admin(self, mock_execute, mock_load_config):
        query = """
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

        args = Namespace(env="dev")
        with mock.patch("croud.projects.commands.print_query") as mock_print:
            projects_list(args)
            assert_query(mock_print, query)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "execute")
class TestProjectsUsers:
    def test_add(self, mock_execute, mock_load_config):
        mutation = """
    mutation {
        addUserToProject(input: {
            projectId: "project-id",
            user: "user-email-or-id"
        }) {
            success
        }
    }
    """

        args = Namespace(
            env="dev",
            project_id="project-id",
            user="user-email-or-id",
            output_fmt="json",
        )
        with mock.patch("croud.projects.users.commands.print_query") as mock_print:
            project_user_add(args)
            assert_query(mock_print, mutation)

    def test_remove(self, mock_execute, mock_load_config):
        mutation = """
    mutation {
        removeUserFromProject(input: {
            projectId: "project-id",
            user: "user-email-or-id"
        }) {
            success
        }
    }
    """

        args = Namespace(
            env="dev",
            project_id="project-id",
            user="user-email-or-id",
            output_fmt="json",
        )
        with mock.patch("croud.projects.users.commands.print_query") as mock_print:
            project_user_remove(args)
            assert_query(mock_print, mutation)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "execute")
class TestUsersRoles:
    def test_add_superuser(self, mock_execute, mock_load_config):
        input_args = f'{{userId: "123",roleFqn: "admin",resourceId: "abc"}}'
        mutation = f"""
    mutation {{
        addRoleToUser(input: {input_args}) {{
            success
        }}
    }}
    """

        args = Namespace(
            env="dev", output_fmt="json", resource="abc", role="admin", user="123"
        )
        with mock.patch("croud.users.roles.commands.print_query") as mock_print:
            roles_add(args)
            assert_query(mock_print, mutation)

    def test_remove(self, mock_query, mock_load_config):
        input_args = '{userId: "123",roleFqn: "org_member",resourceId: "abc"}'
        mutation = f"""
    mutation {{
        removeRoleFromUser(input: {input_args}) {{
            success
        }}
    }}
    """

        args = Namespace(
            env="dev", output_fmt="json", resource="abc", role="org_member", user="123"
        )
        with mock.patch("croud.users.roles.commands.print_query") as mock_print:
            roles_remove(args)
            assert_query(mock_print, mutation)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "execute")
class TestRoles:
    def test_list(self, mock_execute, mock_load_config):
        query = """
    {
        allRoles {
            data {
                fqn
                friendlyName
            }
        }
    }
    """

        args = Namespace(env="dev")
        with mock.patch("croud.users.roles.commands.print_query") as mock_print:
            roles_list(args)
            assert_query(mock_print, query)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "execute")
class TestUsers:
    def test_list_no_filter(self, mock_execute, mock_load_config):
        query = """
    {
        allUsers {
            data {
                uid
                email
                username
            }
        }
    }
    """

        args = Namespace(env=None, no_org=False, org_id=None, output_fmt=None)
        with mock.patch("croud.users.commands.print_query") as mock_print:
            users_list(args)
            assert_query(mock_print, query)

    def test_list_org_filter(self, mock_execute, mock_load_config):
        query = """
    {
        allUsers(queryArgs: {organizationId: "abc"}) {
            data {
                uid
                email
                username
            }
        }
    }
    """

        args = Namespace(env=None, no_org=False, org_id="abc", output_fmt=None)
        with mock.patch("croud.users.commands.print_query") as mock_print:
            users_list(args)
            assert_query(mock_print, query)

    def test_list_no_org_filter(self, mock_execute, mock_load_config):
        query = """
    {
        allUsers(queryArgs: {noOrg: true}) {
            data {
                uid
                email
                username
            }
        }
    }
    """

        args = Namespace(env=None, no_org=True, org_id=None, output_fmt=None)
        with mock.patch("croud.users.commands.print_query") as mock_print:
            users_list(args)
            assert_query(mock_print, query)

    def test_list_filter_dont_conflict(self, mock_execute, mock_load_config):
        query = """
    {
        allUsers(queryArgs: {organizationId: "abc"}) {
            data {
                uid
                email
                username
            }
        }
    }
    """

        args = Namespace(env=None, no_org=True, org_id="abc", output_fmt=None)
        with mock.patch("croud.users.commands.print_query") as mock_print:
            users_list(args)
            assert_query(mock_print, query)


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "execute")
class TestProducts:
    def test_deploy_product(self, mock_execute, mock_load_config):
        mutation = """
mutation {
    createProduct(
        tier: "s1",
        unit: 0,
        projectId: "proj_id",
        name: "test_product",
        cluster: {
            version: "3.1.6",
            username: "crate",
            password: "crate"
        },
        consumer: {
            eventhub: {
                connectionString: "string_connection_eventh",
                consumerGroup: "group_consumer_eventh",
                leaseStorage: {
                    connectionString: "str_conn_storage_lease",
                    container: "container_storage_lease"
                }
            },
            schema: "schema_consumer",
            table: "table_consumer"
        }
    ) {
        id,
        url
    }
}
    """

        args = Namespace(
            env="dev",
            tier="s1",
            unit=0,
            project_id="proj_id",
            product_name="test_product",
            version="3.1.6",
            username="crate",
            password="crate",
            consumer_eventhub_connection_string="string_connection_eventh",
            consumer_eventhub_consumer_group="group_consumer_eventh",
            consumer_eventhub_lease_storage_connection_string="str_conn_storage_lease",
            consumer_eventhub_lease_storage_container="container_storage_lease",
            consumer_schema="schema_consumer",
            consumer_table="table_consumer",
            output_fmt="table",
        )
        with mock.patch("croud.products.deploy.print_query") as mock_print:
            product_deploy(args)
            assert_query(mock_print, mutation)
            assert mock_print.call_args[0][0]._endpoint == "/product/graphql"


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Query, "run", return_value={"data": []})
class TestConsumerSets(CommandTestCase):
    def test_consumer_sets_list(self, mock_run, mock_load_config):

        expected_body = dedent(
            """
    query allConsumerSets($clusterId: String, $productId: String, $projectId: String) {
        allConsumerSets(clusterId: $clusterId, productId: $productId, projectId: $projectId) {
            id
            name
            projectId
            instances
            config {
                cluster {
                    id
                    schema
                    table
                }
                consumerGroup
                leaseStorageContainer
            }
        }
    }
    """  # noqa
        ).strip()

        project_id = gen_uuid()
        product_id = gen_uuid()
        cluster_id = gen_uuid()

        expected_vars = {
            "projectId": project_id,
            "productId": product_id,
            "clusterId": cluster_id,
        }

        argv = [
            "croud",
            "consumer-sets",
            "list",
            "--project-id",
            project_id,
            "--cluster-id",
            cluster_id,
            "--product-id",
            product_id,
        ]

        self.assertGql(mock_run, argv, expected_body, expected_vars)

    def test_consumer_sets_edit(self, mock_run, mock_load_config):
        expected_body = dedent(
            """
    mutation editConsumerSet($id: String!, $input: EditConsumerSetInput!) {
        editConsumerSet(
            id: $id,
            input: $input
        ) {
            id
        }
    }
    """  # noqa
        ).strip()

        consumer_set_id = gen_uuid()

        expected_vars = {
            "id": consumer_set_id,
            "input": {
                "eventhub": {
                    "connectionString": "Endpoint=sb://myhub.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=...",  # noqa
                    "consumerGroup": "$Default",
                    "leaseStorage": {
                        "connectionString": "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net",  # noqa
                        "container": "lease_container",
                    },
                },
                "cluster": {"schema": "doc", "table": "raw"},
            },
        }

        argv = [
            "croud",
            "consumer-sets",
            "edit",
            "--consumer-set-id",
            consumer_set_id,
            "--consumer-eventhub-connection-string",
            "Endpoint=sb://myhub.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=...",  # noqa
            "--consumer-eventhub-consumer-group",
            "$Default",
            "--consumer-eventhub-lease-storage-connection-string",
            "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net",  # noqa
            "--consumer-eventhub-lease-storage-container",
            "lease_container",
            "--consumer-schema",
            "doc",
            "--consumer-table",
            "raw",
        ]

        self.assertGql(mock_run, argv, expected_body, expected_vars)
