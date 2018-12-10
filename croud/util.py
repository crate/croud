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

import asyncio
import os
import platform
import subprocess
import webbrowser
from argparse import Namespace
from typing import Tuple

from croud.config import Configuration
from croud.printer import print_error, print_format, print_info
from croud.session import HttpSession
from croud.typing import JsonDict


# This function was copied from the <https://github.com/Azure/azure-cli>
# project. See `LICENSE` for more information.
def can_launch_browser() -> bool:
    platform_name, release = get_platform_info()
    if is_wsl(platform_name, release) or platform_name != "linux":
        return True
    gui_env_vars = ["DESKTOP_SESSION", "XDG_CURRENT_DESKTOP", "DISPLAY"]
    result = True
    if platform_name == "linux":
        if any(os.getenv(v) for v in gui_env_vars):
            try:
                default_browser = webbrowser.get()
                if (
                    getattr(default_browser, "name", None) == "www-browser"
                ):  # text browser won't work
                    result = False
            except webbrowser.Error:
                result = False
        else:
            result = False

    return result


# This function was copied from the <https://github.com/Azure/azure-cli>
# project. See `LICENSE` for more information.
def is_wsl(platform_name: str, release: str) -> bool:
    platform_name, release = get_platform_info()
    return platform_name == "linux" and release.split("-")[-1] == "microsoft"


# This function was copied from the <https://github.com/Azure/azure-cli>
# project. See `LICENSE` for more information.
def get_platform_info() -> Tuple[str, str]:
    uname = platform.uname()
    platform_name = getattr(uname, "system", None) or uname[0]
    release = getattr(uname, "release", None) or uname[2]
    return platform_name.lower(), release.lower()


# This function was copied from the <https://github.com/Azure/azure-cli>
# project. See `LICENSE` for more information.
def open_page_in_browser(url: str) -> int:
    platform_name, release = get_platform_info()
    if is_wsl(platform_name, release):  # windows 10 linux subsystem
        try:
            return subprocess.call(
                ["cmd.exe", "/c", "start {}".format(url.replace("&", "^&"))]
            )
        except FileNotFoundError:  # WSL might be too old
            pass
    return webbrowser.open_new_tab(url)


def get_entity_list(query: str, args: Namespace, data_key: str) -> None:
    if args.env is not None:
        Configuration.override_context(args.env)

    async def fetch_data() -> JsonDict:
        async with HttpSession(env, token, region) as session:
            return await session.fetch(query)

    env = Configuration.get_env()
    token = Configuration.get_token()
    region = args.region or ""

    loop = asyncio.get_event_loop()
    rows = loop.run_until_complete(fetch_data())

    if rows:
        if isinstance(rows, dict):
            data = rows[data_key]
            # some queries have two levels to access data
            # e.g. {allProjects: {data: [{projects}]}} vs. {me: {data})
            if "data" in data:
                data = data["data"]

            if len(data) == 0:
                print_no_data()
            else:
                print_format(data, args.output_fmt)
        else:
            print_error("Result has no proper format to print.")
    else:
        print_no_data()


def print_no_data():
    print_info("Result contained no data to print.")
