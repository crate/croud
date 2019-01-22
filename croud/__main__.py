#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#
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

import colorama

from croud.clusters.list import clusters_list
from croud.cmd import (
    CMD,
    org_name_arg,
    org_plan_type_arg,
    output_fmt_arg,
    project_id_arg,
    region_arg,
    resource_id_arg,
    role_fqn_arg,
    user_id_arg,
)
from croud.config import Configuration, config_get, config_set
from croud.login import login
from croud.logout import logout
from croud.me import me
from croud.organizations.create import organizations_create
from croud.organizations.list import organizations_list
from croud.projects.list import projects_list
from croud.users.roles.add import roles_add
from croud.users.roles.list import roles_list
from croud.users.roles.remove import roles_remove


def main():
    Configuration.create()
    colorama.init()

    commands: dict = {
        "me": {
            "help": "Prints information about the current logged in user.",
            "extra_args": [output_fmt_arg],
            "calls": me,
        },
        "login": {"help": "Log in to CrateDB Cloud.", "calls": login},
        "logout": {"help": "Log out from CrateDB Cloud.", "calls": logout},
        "config": {
            "help": "Manage croud default configuration values.",
            "sub_commands": {
                "get": {
                    "help": "Get default configuration values.",
                    "calls": config_get,
                    "noop_arg": {"choices": ["env", "region", "output-fmt"]},
                },
                "set": {
                    "help": "Set default configuration values.",
                    "extra_args": [output_fmt_arg, region_arg],
                    "calls": config_set,
                },
            },
        },
        "projects": {
            "help": "Manage CrateDB Cloud projects.",
            "sub_commands": {
                "list": {
                    "help": "Lists all projects for the current "
                    "user in the specified region.",
                    "extra_args": [output_fmt_arg, region_arg],
                    "calls": projects_list,
                }
            },
        },
        "clusters": {
            "help": "Manage CrateDB Cloud clusters.",
            "sub_commands": {
                "list": {
                    "help": "List all clusters for the current user.",
                    "extra_args": [output_fmt_arg, project_id_arg, region_arg],
                    "calls": clusters_list,
                }
            },
        },
        "organizations": {
            "help": "Manage CrateDB Cloud organizations.",
            "sub_commands": {
                "create": {
                    "help": "Creates an organization.",
                    "extra_args": [output_fmt_arg, org_name_arg, org_plan_type_arg],
                    "calls": organizations_create,
                },
                "list": {
                    "help": "List all organizations for the logged in user.",
                    "extra_args": [output_fmt_arg],
                    "calls": organizations_list,
                },
            },
        },
        "users": {
            "help": "Manage CrateDB Cloud users.",
            "sub_commands": {
                "roles": {
                    "help": "Manage CrateDB Cloud user roles.",
                    "sub_commands": {
                        "add": {
                            "help": "Adds a role to a user.",
                            "extra_args": [
                                lambda parser: resource_id_arg(parser, True),
                                lambda parser: user_id_arg(parser, True),
                                output_fmt_arg,
                                role_fqn_arg,
                            ],
                            "calls": roles_add,
                        },
                        "remove": {
                            "help": "Removes a role from a user.",
                            "extra_args": [
                                lambda parser: resource_id_arg(parser, True),
                                lambda parser: user_id_arg(parser, True),
                                output_fmt_arg,
                                role_fqn_arg,
                            ],
                            "calls": roles_remove,
                        },
                        "list": {
                            "help": "Lists all available roles.",
                            "extra_args": [output_fmt_arg],
                            "calls": roles_list,
                        },
                    },
                }
            },
        },
    }
    croud_cmd = CMD()
    croud_cmd.create_parent_cmd(1, commands)


if __name__ == "__main__":
    main()
