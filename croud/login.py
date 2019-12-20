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

from argparse import Namespace
from functools import partial
from typing import Optional

from croud.api import Client, construct_api_base_url
from croud.config import Configuration
from croud.printer import print_error, print_info, print_warning
from croud.server import Server
from croud.util import can_launch_browser, open_page_in_browser

LOGIN_PATH = "/oauth2/login?cli=true"


def get_org_id() -> Optional[str]:
    client = Client(
        env=Configuration.get_env(), region=Configuration.get_setting("region")
    )
    data, error = client.get("/api/v2/users/me/")
    if data and not error:
        return data.get("organization_id")
    return None


def login(args: Namespace) -> None:
    """
    Performs an OAuth2 Login to CrateDB Cloud
    """

    if not can_launch_browser():
        print_error("Login only works with a valid browser installed.")
        exit(1)

    env = args.env or Configuration.get_env()
    Configuration.set_context(env.lower())
    server = Server(partial(Configuration.set_token, env=env)).start_in_background()
    open_page_in_browser(_login_url(env))
    print_info("A browser tab has been launched for you to login.")
    try:
        # Wait for the user to login. They'll be redirected to the `SetTokenHandler`
        # which will set the token in the configuration.
        server.wait_for_shutdown()
    except (KeyboardInterrupt, SystemExit):
        print_warning("Login cancelled.")
    else:
        organization_id = get_org_id()
        if organization_id:
            Configuration.set_organization_id(organization_id, env)
        else:
            Configuration.set_organization_id("", env)

        print_info("Login successful.")


def _login_url(env: str) -> str:
    return construct_api_base_url(env.lower()) + LOGIN_PATH
