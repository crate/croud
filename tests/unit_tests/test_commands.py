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
from argparse import ArgumentParser, Namespace
from unittest import mock

import pytest
from util import CommandTestCase

from croud.config import Configuration, config_get, config_set
from croud.organizations.users.commands import (
    role_fqn_transform as organization_role_fqn_transform,
)
from croud.projects.users.commands import (
    role_fqn_transform as project_role_fqn_transform,
)
from croud.rest import Client
from croud.session import RequestMethod
from croud.users.commands import transform_roles_list


def gen_uuid() -> str:
    return str(uuid.uuid4())


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
class TestMe(CommandTestCase):
    def test_me(self, mock_send, mock_config):
        argv = ["croud", "me"]
        self.assertRest(mock_send, argv, RequestMethod.GET, "/api/v2/users/me/")


class TestConfigGet:
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_get_env(self, mock_print, mock_load_config):
        config_get(Namespace(get="env", output_fmt=None))
        mock_print.assert_called_once_with(
            textwrap.dedent(
                """
                +-------+
                | env   |
                |-------|
                | prod  |
                +-------+
            """
            ).strip()
        )

    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    @mock.patch("builtins.print", autospec=True, side_effect=print)
    def test_get_top_level_setting(self, mock_print, mock_load_config):
        config_get(Namespace(get="region", output_fmt=None))
        mock_print.assert_called_once_with(
            textwrap.dedent(
                """
                +------------+
                | region     |
                |------------|
                | bregenz.a1 |
                +------------+
            """
            ).strip()
        )


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

    @mock.patch("croud.config.write_config")
    @mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
    def test_set_no_arguments(self, mock_load_config, mock_write_config, capsys):
        config = Configuration.DEFAULT_CONFIG
        config["auth"]["current_context"] = "prod"

        config_set(Namespace(), parser=ArgumentParser(usage="Some help text"))
        out, _ = capsys.readouterr()
        assert "Some help text" in out
        mock_write_config.assert_not_called()


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class TestClusters(CommandTestCase):
    project_id = gen_uuid()

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list_no_project_id(self, mock_send, mock_load_config):
        argv = ["croud", "clusters", "list"]
        self.assertRest(
            mock_send, argv, RequestMethod.GET, "/api/v2/clusters/", params={}
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list_with_project_id(self, mock_send, mock_load_config):
        argv = ["croud", "clusters", "list", "--project-id", self.project_id]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.GET,
            "/api/v2/clusters/",
            params={"project_id": self.project_id},
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_deploy_cluster(self, mock_send, mock_load_config):
        argv = [
            "croud",
            "clusters",
            "deploy",
            "--product-name",
            "cratedb.az1",
            "--tier",
            "xs",
            "--unit",
            "1",
            "--project-id",
            self.project_id,
            "--cluster-name",
            "crate_cluster",
            "--version",
            "3.2.5",
            "--username",
            "foobar",
            "--password",
            "s3cr3t!",
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/clusters/",
            body={
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "product_unit": 1,
                "project_id": self.project_id,
                "username": "foobar",
                "channel": "stable",
            },
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_deploy_cluster_no_unit(self, mock_send, mock_load_config):
        argv = [
            "croud",
            "clusters",
            "deploy",
            "--product-name",
            "cratedb.az1",
            "--tier",
            "xs",
            "--project-id",
            self.project_id,
            "--cluster-name",
            "crate_cluster",
            "--version",
            "3.2.5",
            "--username",
            "foobar",
            "--password",
            "s3cr3t!",
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/clusters/",
            body={
                "crate_version": "3.2.5",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "project_id": self.project_id,
                "username": "foobar",
                "channel": "stable",
            },
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_deploy_cluster_nightly(self, mock_send, mock_load_config):
        argv = [
            "croud",
            "clusters",
            "deploy",
            "--product-name",
            "cratedb.az1",
            "--tier",
            "xs",
            "--unit",
            "1",
            "--project-id",
            self.project_id,
            "--cluster-name",
            "crate_cluster",
            "--version",
            "nightly-4.1.0-20190712",
            "--username",
            "foobar",
            "--password",
            "s3cr3t!",
            "--channel",
            "nightly",
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/clusters/",
            body={
                "crate_version": "nightly-4.1.0-20190712",
                "name": "crate_cluster",
                "password": "s3cr3t!",
                "product_name": "cratedb.az1",
                "product_tier": "xs",
                "project_id": self.project_id,
                "username": "foobar",
                "channel": "nightly",
                "product_unit": 1,
            },
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_scale_cluster(self, mock_send, mock_load_config):
        unit = 1
        cluster_id = gen_uuid()
        argv = ["croud", "clusters", "scale", "--cluster-id", cluster_id, "--unit", "1"]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.PUT,
            f"/api/v2/clusters/{cluster_id}/scale/",
            body={"product_unit": unit},
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_upgrade_cluster(self, mock_send, mock_load_config):
        version = "3.2.6"
        cluster_id = gen_uuid()
        argv = [
            "croud",
            "clusters",
            "upgrade",
            "--cluster-id",
            cluster_id,
            "--version",
            version,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.PUT,
            f"/api/v2/clusters/{cluster_id}/upgrade/",
            body={"crate_version": version},
        )

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_clusters_delete(self, mock_send, mock_load_config, capsys):
        cluster_id = gen_uuid()
        argv = ["croud", "clusters", "delete", "--cluster-id", cluster_id]
        with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
            self.assertRest(
                mock_send, argv, RequestMethod.DELETE, f"/api/v2/clusters/{cluster_id}/"
            )
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the cluster? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Cluster deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_clusters_delete_flag(self, mock_send, mock_load_config, capsys):
        cluster_id = gen_uuid()
        argv = ["croud", "clusters", "delete", "--cluster-id", cluster_id, "-y"]
        with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
            self.assertRest(
                mock_send, argv, RequestMethod.DELETE, f"/api/v2/clusters/{cluster_id}/"
            )
            mock_input.assert_not_called()

        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Cluster deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_clusters_delete_aborted(self, mock_send, mock_load_config, capsys):
        cluster_id = gen_uuid()
        argv = ["croud", "clusters", "delete", "--cluster-id", cluster_id]
        with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
            self.execute(argv)
            mock_send.assert_not_called()
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the cluster? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Cluster deletion cancelled." in err_output


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class TestOrganizations(CommandTestCase):
    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_create(self, mock_send, mock_load_config):
        argv = ["croud", "organizations", "create", "--name", "test-org"]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/organizations/",
            body={"name": "test-org"},
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_create_name_plan_type(self, mock_send, mock_load_config):
        argv = [
            "croud",
            "organizations",
            "create",
            "--name",
            "test-org",
            "--plan-type",
            "3",
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/organizations/",
            body={"name": "test-org", "plan_type": 3},
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_edit_name(self, mock_send, mock_load_config):
        org_id = gen_uuid()
        argv = [
            "croud",
            "organizations",
            "edit",
            "--name",
            "new-org-name",
            "--org-id",
            org_id,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.PUT,
            f"/api/v2/organizations/{org_id}/",
            body={"name": "new-org-name"},
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_edit_plan_type(self, mock_send, mock_load_config):
        org_id = gen_uuid()
        argv = [
            "croud",
            "organizations",
            "edit",
            "--plan-type",
            "3",
            "--org-id",
            org_id,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.PUT,
            f"/api/v2/organizations/{org_id}/",
            body={"plan_type": 3},
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_edit_name_plan_type(self, mock_send, mock_load_config):
        org_id = gen_uuid()
        argv = [
            "croud",
            "organizations",
            "edit",
            "--name",
            "new-org-name",
            "--plan-type",
            "3",
            "--org-id",
            org_id,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.PUT,
            f"/api/v2/organizations/{org_id}/",
            body={"name": "new-org-name", "plan_type": 3},
        )

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_edit_no_arguments(self, mock_send, mock_load_config, capsys):
        org_id = gen_uuid()
        argv = ["croud", "organizations", "edit", "--org-id", org_id]
        with pytest.raises(SystemExit):
            self.assertRest(
                mock_send, argv, RequestMethod.PUT, f"/api/v2/organizations/{org_id}/"
            )
        _, err = capsys.readouterr()
        assert "No input arguments found." in err

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list(self, mock_send, mock_load_config):
        argv = ["croud", "organizations", "list"]
        self.assertRest(mock_send, argv, RequestMethod.GET, "/api/v2/organizations/")

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete(self, mock_send, mock_load_config, capsys):
        org_id = gen_uuid()
        argv = ["croud", "organizations", "delete", "--org-id", org_id]
        with mock.patch("builtins.input", side_effect=["Y"]) as mock_input:
            self.assertRest(
                mock_send,
                argv,
                RequestMethod.DELETE,
                f"/api/v2/organizations/{org_id}/",
            )
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the organization? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Organization deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete_flag(self, mock_send, mock_load_config, capsys):
        org_id = gen_uuid()
        argv = ["croud", "organizations", "delete", "--org-id", org_id, "-y"]
        with mock.patch("builtins.input") as mock_input:
            self.assertRest(
                mock_send,
                argv,
                RequestMethod.DELETE,
                f"/api/v2/organizations/{org_id}/",
            )
            mock_input.assert_not_called()

        _, err_output = capsys.readouterr()
        assert "Organization deleted." in err_output

    @pytest.mark.parametrize("input", ["", "N", "No", "cancel"])
    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete_aborted(self, mock_send, mock_load_config, capsys, input):
        org_id = gen_uuid()
        argv = ["croud", "organizations", "delete", "--org-id", org_id]
        with mock.patch("builtins.input", side_effect=[input]) as mock_input:
            self.execute(argv)
            mock_send.assert_not_called()
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the organization? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Organization deletion cancelled." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete_aborted_with_input(self, mock_send, mock_load_config, capsys):
        org_id = gen_uuid()
        argv = ["croud", "organizations", "delete", "--org-id", org_id]
        with mock.patch("builtins.input", side_effect=["N"]) as mock_input:
            self.execute(argv)
            mock_send.assert_not_called()
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the organization? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Organization deletion cancelled." in err_output

    @mock.patch.object(Client, "send", return_value=({"added": True}, None))
    def test_add_user(self, mock_send, mock_load_config):
        org_id = gen_uuid()
        user = "test@crate.io"
        role_fqn = "org_admin"

        argv = [
            "croud",
            "organizations",
            "users",
            "add",
            "--user",
            user,
            "--org-id",
            org_id,
            "--role",
            role_fqn,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            f"/api/v2/organizations/{org_id}/users/",
            body={"user": user, "role_fqn": role_fqn},
        )

    @mock.patch.object(Client, "send", return_value=({"added": False}, None))
    def test_update_user(self, mock_send, mock_load_confg, capsys):
        org_id = gen_uuid()
        user = "test@crate.io"
        role_fqn = "org_admin"

        argv = [
            "croud",
            "organizations",
            "users",
            "add",
            "--user",
            user,
            "--org-id",
            org_id,
            "--role",
            role_fqn,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            f"/api/v2/organizations/{org_id}/users/",
            body={"user": user, "role_fqn": role_fqn},
        )
        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Role altered for user." in err_output

    def test_role_fqn_transform(self, mock_load_config):
        user = {
            "organization_roles": [
                {"organization_id": "org-1", "role_fqn": "organization_admin"},
                {"organization_id": "org-2", "role_fqn": "organization_member"},
                {"organization_id": "org-3", "role_fqn": "organization_member"},
            ]
        }
        response = organization_role_fqn_transform(user["organization_roles"])
        assert response == "organization_admin"

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list_user(self, mock_send, mock_load_config):
        org_id = gen_uuid()

        argv = ["croud", "organizations", "users", "list", "--org-id", org_id]
        self.assertRest(
            mock_send, argv, RequestMethod.GET, f"/api/v2/organizations/{org_id}/users/"
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_remove_user(self, mock_send, mock_load_config):
        org_id = gen_uuid()
        user = "test@crate.io"

        argv = [
            "croud",
            "organizations",
            "users",
            "remove",
            "--user",
            user,
            "--org-id",
            org_id,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.DELETE,
            f"/api/v2/organizations/{org_id}/users/{user}/",
        )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class TestProjects(CommandTestCase):
    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_create(self, mock_send, mock_load_config):
        argv = [
            "croud",
            "projects",
            "create",
            "--name",
            "new-project",
            "--org-id",
            "organization-id",
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            "/api/v2/projects/",
            body={"name": "new-project", "organization_id": "organization-id"},
        )

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete(self, mock_send, mock_load_config, capsys):
        project_id = gen_uuid()
        argv = ["croud", "projects", "delete", "--project-id", project_id]
        with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
            self.assertRest(
                mock_send, argv, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/"
            )
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the project? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Project deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete_flag(self, mock_send, mock_load_config, capsys):
        project_id = gen_uuid()
        argv = ["croud", "projects", "delete", "--project-id", project_id, "-y"]
        with mock.patch("builtins.input", side_effect=["y"]) as mock_input:
            self.assertRest(
                mock_send, argv, RequestMethod.DELETE, f"/api/v2/projects/{project_id}/"
            )
            mock_input.assert_not_called()

        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Project deleted." in err_output

    @mock.patch.object(Client, "send", return_value=(None, {}))
    def test_delete_aborted(self, mock_send, mock_load_config, capsys):
        project_id = gen_uuid()
        argv = ["croud", "projects", "delete", "--project-id", project_id]
        with mock.patch("builtins.input", side_effect=["Nooooo"]) as mock_input:
            self.execute(argv)
            mock_send.assert_not_called()
            mock_input.assert_called_once_with(
                "Are you sure you want to delete the project? [yN] "
            )

        _, err_output = capsys.readouterr()
        assert "Project deletion cancelled." in err_output

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list(self, mock_send, mock_load_config):
        argv = ["croud", "projects", "list"]
        self.assertRest(mock_send, argv, RequestMethod.GET, "/api/v2/projects/")


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
class TestProjectsUsers(CommandTestCase):
    def test_role_fqn_transform(self, mock_load_config):
        user = {
            "project_roles": [
                {"project_id": "project-1", "role_fqn": "project_admin"},
                {"project_id": "project-2", "role_fqn": "project_member"},
                {"project_id": "project-3", "role_fqn": "project_member"},
            ]
        }
        response = project_role_fqn_transform(user["project_roles"])
        assert response == "project_admin"

    @mock.patch.object(Client, "send", return_value=({"added": True}, None))
    def test_add(self, mock_send, mock_load_config):
        project_id = gen_uuid()

        # uid or email would be possible for the backend
        user = "test@crate.io"
        role_fqn = "project_admin"

        argv = [
            "croud",
            "projects",
            "users",
            "add",
            "--project-id",
            project_id,
            "--user",
            user,
            "--role",
            role_fqn,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            f"/api/v2/projects/{project_id}/users/",
            body={"user": user, "role_fqn": role_fqn},
        )

    @mock.patch.object(Client, "send", return_value=({"added": False}, None))
    def test_update(self, mock_send, mock_load_config, capsys):
        project_id = gen_uuid()
        user = "test@crate.io"
        role_fqn = "project_admin"

        argv = [
            "croud",
            "projects",
            "users",
            "add",
            "--project-id",
            project_id,
            "--user",
            user,
            "--role",
            role_fqn,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.POST,
            f"/api/v2/projects/{project_id}/users/",
            body={"user": user, "role_fqn": role_fqn},
        )
        _, err_output = capsys.readouterr()
        assert "Success" in err_output
        assert "Role altered for user." in err_output

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_list(self, mock_send, mock_load_config):
        project_id = gen_uuid()

        argv = ["croud", "projects", "users", "list", "--project-id", project_id]
        self.assertRest(
            mock_send, argv, RequestMethod.GET, f"/api/v2/projects/{project_id}/users/"
        )

    @mock.patch.object(Client, "send", return_value=({}, None))
    def test_remove(self, mock_send, mock_load_config):
        project_id = gen_uuid()

        # uid or email would be possible for the backend
        user = "test@crate.io"

        argv = [
            "croud",
            "projects",
            "users",
            "remove",
            "--project-id",
            project_id,
            "--user",
            user,
        ]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.DELETE,
            f"/api/v2/projects/{project_id}/users/{user}/",
        )


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
class TestUsersRolesREST(CommandTestCase):
    def test_list(self, mock_send, mock_load_config):
        argv = ["croud", "users", "roles", "list"]

        self.assertRest(mock_send, argv, RequestMethod.GET, "/api/v2/roles/")


@mock.patch("croud.config.load_config", return_value=Configuration.DEFAULT_CONFIG)
@mock.patch.object(Client, "send", return_value=({}, None))
class TestUsers(CommandTestCase):
    def test_list(self, mock_send, mock_load_config):
        argv = ["croud", "users", "list"]
        self.assertRest(
            mock_send, argv, RequestMethod.GET, "/api/v2/users/", params=None
        )

    def test_transform_roles_list(self, mock_send, mock_load_config):
        user = {
            "organization_roles": [
                {"organization_id": "org-1", "role_fqn": "org_admin"},
                {"organization_id": "org-2", "role_fqn": "org_member"},
                {"organization_id": "org-3", "role_fqn": "org_member"},
            ],
            "project_roles": [
                {"project_id": "project-1", "role_fqn": "project_admin"},
                {"project_id": "project-2", "role_fqn": "project_member"},
                {"project_id": "project-3", "role_fqn": "project_member"},
            ],
        }
        response = transform_roles_list("organization_id")(user["organization_roles"])
        assert response == "org-1: org_admin,\norg-2: org_member,\norg-3: org_member"
        response = transform_roles_list("project_id")(user["project_roles"])
        assert response == (
            "project-1: project_admin,\n"
            "project-2: project_member,\n"
            "project-3: project_member"
        )

    def test_list_no_org(self, mock_send, mock_load_config, capsys):
        argv = ["croud", "users", "list", "--no-org"]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.GET,
            "/api/v2/users/",
            params={"no-roles": "1"},
        )
        _, err = capsys.readouterr()
        assert (
            "The --no-org argument is deprecated. Please use --no-roles instead." in err
        )

    def test_list_no_roles(self, mock_send, mock_load_config):
        argv = ["croud", "users", "list", "--no-roles"]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.GET,
            "/api/v2/users/",
            params={"no-roles": "1"},
        )

    def test_list_no_org_no_roles(self, mock_send, mock_load_config, capsys):
        argv = ["croud", "users", "list", "--no-roles", "--no-org"]
        self.assertRest(
            mock_send,
            argv,
            RequestMethod.GET,
            "/api/v2/users/",
            params={"no-roles": "1"},
        )
        _, err = capsys.readouterr()
        assert (
            "The --no-org argument is deprecated. Please use --no-roles instead." in err
        )


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
            self.execute(argv)
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
