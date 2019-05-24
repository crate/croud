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

import functools
import os
import platform
import subprocess
import webbrowser
from argparse import Namespace
from typing import Dict, Tuple

from croud.printer import print_info


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


def clean_dict(data: Dict) -> Dict:
    """Clean a dictionary recursively from keys with None values.
    Returns a new instance of a dict.
    """
    cleaned = {}
    for k, v in data.items():
        if v is None:
            continue
        elif isinstance(v, dict):
            cleaned[k] = clean_dict(v)
        else:
            cleaned[k] = v
    return cleaned


def confirm_prompt(msg):
    msg = f"{msg.rstrip()} [yN] "
    resp = input(msg).lower()
    return resp in {"y", "yes"}


def require_confirmation(
    confirm_msg: str, cancel_msg="Command aborted!"
):  # decorator setup
    def _inner(cmd):  # decorator
        @functools.wraps(cmd)
        def _wrapper(cmd_args: Namespace):  # decorator logic
            is_confirmed = cmd_args.yes
            if not is_confirmed:
                is_confirmed = confirm_prompt(confirm_msg)
            if is_confirmed:
                cmd(cmd_args)
            else:
                print_info(cancel_msg)

        return _wrapper

    return _inner
