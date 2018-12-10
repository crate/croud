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
from croud.cmd import CMD, output_fmt_arg, project_id_arg, region_arg
from croud.config import Configuration
from croud.env import env
from croud.login import login
from croud.logout import logout
from croud.me import me
from croud.projects.list import projects_list


def main():
    Configuration.create()
    colorama.init()

    commands: dict = {
        "me": {
            "description": "Prints the current logged in user",
            "extra_args": [output_fmt_arg, region_arg],
            "calls": me,
        },
        "login": {
            "description": "Performs an OAuth2 Login to CrateDB Cloud",
            "calls": login,
        },
        "logout": {
            "description": "Performs a logout of the current logged in user",
            "calls": logout,
        },
        "env": {
            "description": "Switches auth context",
            "sub_commands": {
                "prod": {
                    "description": "Switch auth context to prod",
                    "calls": env("prod"),
                },
                "dev": {
                    "description": "Switch auth context to dev",
                    "calls": env("dev"),
                },
            },
        },
        "projects": {
            "description": "Project sub commands",
            "sub_commands": {
                "list": {
                    "description": "Lists all projects for the current "
                    "user in the specified region",
                    "extra_args": [output_fmt_arg, region_arg],
                    "calls": projects_list,
                }
            },
        },
        "clusters": {
            "description": "Cluster sub commands",
            "sub_commands": {
                "list": {
                    "description": "List all clusters for the current user",
                    "extra_args": [output_fmt_arg, project_id_arg, region_arg],
                    "calls": clusters_list,
                }
            },
        },
    }
    croud_cmd = CMD()
    croud_cmd.create_parent_cmd(1, commands)


if __name__ == "__main__":
    main()
