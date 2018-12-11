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
from croud.config import Configuration
from croud.login import login
from croud.logout import logout
from croud.server import Server


class TestLogin(unittest.TestCase):
    @mock.patch("croud.config.load_config")
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
    ):
        mock_load_config.return_value = Configuration.DEFAULT_CONFIG
        m = mock.mock_open()
        with mock.patch("croud.config.open", m, create=True):
            login(Namespace(env="dev"))

        calls = [
            mock.call("A browser tab has been launched for you to login."),
            mock.call("Login successful."),
        ]
        mock_print_info.assert_has_calls(calls)

    @mock.patch("croud.login.can_launch_browser", return_value=False)
    @mock.patch("croud.login.print_error")
    def test_login_no_valid_browser(self, mock_print_error, mock_can_launch_browser):
        with self.assertRaises(SystemExit) as cm:
            login(Namespace(env="dev"))

        mock_print_error.assert_called_once_with(
            "Login only works with a valid browser installed."
        )
        self.assertEqual(cm.exception.code, 1)


class TestLogout(unittest.TestCase):
    @mock.patch("croud.logout.Configuration.set_token")
    @mock.patch("croud.logout.print_info")
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_logout(self, mock_load_config, mock_print_info, mock_set_token):
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
