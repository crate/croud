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
from typing import Optional

from croud.api import Client
from croud.config import CONFIG
from croud.printer import print_error, print_info, print_warning
from croud.server import Server
from croud.util import can_launch_browser, open_page_in_browser


def login_path(idp: str = None) -> str:
    extra_part = f"{idp}/" if idp else ""
    return f"/oauth2/{extra_part}login?cli=true"


def get_org_id() -> Optional[str]:
    client = Client(CONFIG.endpoint, token=CONFIG.token, region=CONFIG.region)
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

    if CONFIG.key and CONFIG.secret:
        print_warning(
            "Looks like you have an API key and secret set in this profile. "
            "They will be ignored if you log in successfully."
        )

    server = Server(CONFIG.set_current_auth_token).start_in_background()

    open_page_in_browser(CONFIG.endpoint + login_path(args.idp))
    print_info("A browser tab has been launched for you to login.")
    try:
        # Wait for the user to login. They'll be redirected to the `SetTokenHandler`
        # which will set the token in the configuration.
        server.wait_for_shutdown()
    except (KeyboardInterrupt, SystemExit):
        print_warning("Login cancelled.")
    else:
        organization_id = get_org_id()
        CONFIG.set_organization_id(CONFIG.name, organization_id)
        print_info("Login successful.")
        print_info(f"Current profile: {CONFIG.name}")
        print_info(f"API endpoint   : {CONFIG.endpoint}")
        print_info(f"Organization ID: {organization_id}")
