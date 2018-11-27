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

import argh

from croud.config import Configuration
from croud.printer import print_error, print_info
from croud.server import Server
from croud.util import can_launch_browser, open_page_in_browser


@argh.arg("--env", choices=["dev", "prod"], default="prod", type=str)
def login(env=None) -> None:
    """
    Performs an OAuth2 Login to CrateDB Cloud
    """
    if can_launch_browser():
        Configuration.override_context(env.lower())
        loop = asyncio.get_event_loop()
        server = Server(loop)
        server.create_web_app()
        loop.run_until_complete(server.start())

        domain = "cratedb.cloud"
        if env.lower() == "dev":
            domain = "cratedb-dev.cloud"

        login_url = f"https://bregenz.a1.{domain}/oauth2/login?cli=true"
        open_page_in_browser(login_url)
        print_info("A browser tab has been launched for you to login.")

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(server.stop())
            exit(1)
        finally:
            loop.run_until_complete(server.stop())
        loop.close()

        Configuration.set_env(env.lower())
    else:
        print_error("Login only works with a valid browser installed.")
        exit(1)

    print_info("Login successful.")
