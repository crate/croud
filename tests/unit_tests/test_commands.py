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

from croud.clusters.list import clusters_list
from croud.config import Configuration, config_get, config_set
from croud.login import _login_url, _set_login_env, login
from croud.logout import logout
from croud.organizations.create import organizations_create
from croud.organizations.list import organizations_list
from croud.server import Server
from croud.users.roles.add import roles_add


class TestLogin(unittest.TestCase):
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
        with self.assertRaises(SystemExit) as cm:
            login(Namespace(env=None))

        mock_print_error.assert_called_once_with(
            "Login only works with a valid browser installed."
        )
        self.assertEqual(cm.exception.code, 1)

    @mock.patch("croud.config.Configuration.override_context")
    @mock.patch("croud.config.Configuration.get_env", return_value="dev")
    def test_login_env_from_current_context(self, mock_get_env, mock_override_context):
        env = _set_login_env(None)
        self.assertEqual(env, "dev")

    def test_login_env_override_context_from_argument(self):
        env = _set_login_env("prod")
        self.assertEqual(env, "prod")

    def test_login_urls_from_valid_envs(self):
        url = _login_url("dev")
        self.assertEqual(
            "https://bregenz.a1.cratedb-dev.cloud/oauth2/login?cli=true", url
        )

        url = _login_url("prod")
        self.assertEqual("https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true", url)

        url = _login_url("PROD")
        self.assertEqual("https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true", url)

    def test_env_fallback_url(self):
        url = _login_url("invalid")
        self.assertEqual("https://bregenz.a1.cratedb.cloud/oauth2/login?cli=true", url)


class TestLogout(unittest.TestCase):
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


class TestClustersList(unittest.TestCase):
    @mock.patch("croud.clusters.list.get_entity_list")
    def test_list_clusters_no_pid(self, get_entity_list):
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

        args: Namespace = Namespace(
            env=None, output_fmt="table", project_id=None, region="bregenz.a1"
        )
        clusters_list(args)
        get_entity_list.assert_called_once_with(query, args, "allClusters")

    @mock.patch("croud.clusters.list.get_entity_list")
    def test_list_clusters_pid(self, get_entity_list):
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

        args: Namespace = Namespace(
            env=None,
            output_fmt="table",
            project_id="60d398b4-455b-49dc-bfe9-04edf5bd3eb2",
            region="bregenz.a1",
        )
        clusters_list(args)
        get_entity_list.assert_called_once_with(query, args, "allClusters")


class TestConfigGet(unittest.TestCase):
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


class TestConfigSet(unittest.TestCase):
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


class TestOrganizationsCreate(unittest.TestCase):
    authd_response = {
        "id": "60d398b4-455b-49dc-bfe9-04edf5bd3eb2",
        "name": "testorg",
        "planType": 1,
    }
    unauthd_response = {"errors": [{"message": "Missing privileges"}]}

    @mock.patch("croud.organizations.create.print_error")
    @mock.patch(
        "croud.organizations.create.gql_mutation", return_value=unauthd_response
    )
    def test_create_non_superuser(self, mock_gql_mutation, mock_print_error):
        mutation = """
mutation {
    createOrganization(input: {
        name: \"testorg\",
        planType: 1
    }) {
        id
        name
        planType
    }
}
    """

        args = Namespace(env="dev", name="testorg", output_fmt="json", plan_type=1)
        organizations_create(args)
        mock_gql_mutation.assert_called_once_with(mutation, args, "createOrganization")
        mock_print_error.assert_called_once_with("Missing privileges")

    @mock.patch("croud.organizations.create.print_format")
    @mock.patch("croud.organizations.create.gql_mutation", return_value=authd_response)
    def test_create_superuser(self, mock_gql_mutation, mock_print_format):
        args = Namespace(env="dev", name="testorg", output_fmt="json", plan_type=1)
        organizations_create(args)
        mock_print_format.assert_called_once_with(self.authd_response, "json")


class TestOrganizationsList(unittest.TestCase):
    @mock.patch("croud.organizations.list.get_entity_list")
    def test_list_organizations_no_superuser(self, get_entity_list):
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

        args: Namespace = Namespace()
        organizations_list(args)
        get_entity_list.assert_called_once_with(query, args, "allOrganizations")


class TestUsersRolesAdd(unittest.TestCase):
    authd_response = {
        "user": {
            "uid": "60d398b4-455b-49dc-bfe9-04edf5bd3eb2",
            "email": "test@crate.io",
            "username": "cratey",
            "organizationId": "99d398b4-465b-97dk-bfe9-04edf5ah3ei2",
        }
    }
    unauthd_response = {"errors": [{"message": "Missing privileges"}]}

    res_id = "99d398b4-465b-97dk-bfe9-04edf5ah3ei2"
    role = "admin"
    uid = "60d398b4-455b-49dc-bfe9-04edf5bd3eb2"
    input_args = f'{{userId: "{uid}", roleFqn: "admin", resourceId: "{res_id}"}}'
    mutation = f"""
mutation {{
    assignRoleToUser(input: {input_args}) {{
        user {{
            uid,
            email,
            username,
            organizationId
        }}
    }}
}}
"""

    @mock.patch("croud.users.roles.add.print_error")
    @mock.patch("croud.users.roles.add.gql_mutation", return_value=unauthd_response)
    def test_users_roles_add_no_superuser(self, mock_gql_mutation, mock_print_error):
        args = Namespace(
            env="dev",
            output_fmt="json",
            resource=self.res_id,
            role=self.role,
            user=self.uid,
        )
        roles_add(args)
        mock_gql_mutation.assert_called_once_with(
            self.mutation, args, "assignRoleToUser"
        )
        mock_print_error.assert_called_once_with("Missing privileges")

    @mock.patch("croud.users.roles.add.print_format")
    @mock.patch("croud.users.roles.add.gql_mutation", return_value=authd_response)
    def test_users_roles_add_superuser(self, mock_gql_mutation, mock_print_format):
        args = Namespace(
            env="dev",
            output_fmt="json",
            resource=self.res_id,
            role=self.role,
            user=self.uid,
        )
        roles_add(args)
        mock_print_format.assert_called_once_with(self.authd_response, "json")
