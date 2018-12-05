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

from croud.cmd import CMD, output_fmt_arg, region_arg
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
            "usage": "croud me [-h] [--env {prod,dev}]\n\t\t"
            "[-r {westeurope.azure,eastus.azure,bregenz.a1}] "
            "[-o {json}]",
            "extra_args": [region_arg, output_fmt_arg],
            "calls": me,
        },
        "login": {
            "description": "Performs an OAuth2 Login to CrateDB Cloud",
            "usage": "croud login [-h] [--env {prod,dev}]",
            "calls": login,
        },
        "logout": {
            "description": "Performs a logout of the current logged in user",
            "usage": "croud logout [-h] [--env {prod,dev}]",
            "calls": logout,
        },
        "env": {
            "description": "Switches auth context",
            "usage": "croud env [-h] {prod,dev}",
            "sub_commands": {
                "prod": {
                    "description": "Switch auth context to prod",
                    "usage": "croud env prod",
                    "calls": env,
                },
                "dev": {
                    "description": "Switch auth context to dev",
                    "usage": "croud env dev",
                    "calls": env,
                },
            },
        },
        "projects": {
            "description": "Project sub commands",
            "usage": "croud projects [-h] {list,create}",
            "sub_commands": {
                "list": {
                    "description": "Lists all projects for the current "
                    "user in the specified region",
                    "usage": "croud projects list [-h] [--env {prod,dev}] [-o {json}]",
                    "extra_args": [output_fmt_arg],
                    "calls": projects_list,
                }
            },
        },
    }
    CMD(commands)


if __name__ == "__main__":
    main()
