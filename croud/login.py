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
from argparse import Namespace
from functools import partial
from typing import Optional

from croud.config import Configuration
from croud.printer import print_error, print_info
from croud.rest import Client, RequestMethod
from croud.server import Server
from croud.session import cloud_url
from croud.util import can_launch_browser, open_page_in_browser

LOGIN_PATH = "/oauth2/login?cli=true"


def get_org_id() -> Optional[str]:
    client = Client(
        env=Configuration.get_env(), region=Configuration.get_setting("region")
    )
    data, error = client.send(RequestMethod.GET, "/api/v2/users/me/")
    if data and not error:
        return data.get("organization_id")
    return None


def login(args: Namespace) -> None:
    """
    Performs an OAuth2 Login to CrateDB Cloud
    """

    if can_launch_browser():
        env = args.env or Configuration.get_env()

        loop = asyncio.get_event_loop()
        server = Server(loop)
        server.create_web_app(partial(Configuration.set_token, env=env))
        loop.run_until_complete(server.start())

        open_page_in_browser(_login_url(env))
        print_info("A browser tab has been launched for you to login.")

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(server.stop())
            exit(1)
        finally:
            loop.run_until_complete(server.stop())

        Configuration.set_context(env.lower())

        organization_id = get_org_id()
        if organization_id:
            Configuration.set_organization_id(organization_id, env)
        else:
            Configuration.set_organization_id("", env)

        loop.close()

    else:
        print_error("Login only works with a valid browser installed.")
        exit(1)

    print_info("Login successful.")


def _login_url(env: str) -> str:
    return cloud_url(env.lower()) + LOGIN_PATH
