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

from croud.config import Configuration
from croud.printer import print_info
from croud.session import HttpSession, cloud_url

LOGOUT_PATH = "/oauth2/logout"


def logout(args: Namespace) -> None:
    loop = asyncio.get_event_loop()
    env = args.env or Configuration.get_env()
    token = Configuration.get_token(env)

    loop.run_until_complete(make_request(env, token))
    Configuration.set_token("", env)

    print_info("You have been logged out.")


async def make_request(env: str, token: str) -> None:
    async with HttpSession(env, token) as session:
        await session.logout(_logout_url(env))


def _logout_url(env: str) -> str:
    return cloud_url(env) + LOGOUT_PATH
