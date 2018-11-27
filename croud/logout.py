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
from croud.printer import print_info
from croud.session import HttpSession


@argh.arg("--env", choices=["prod", "dev"], default=None, type=str)
def logout(env=None) -> None:
    """
    Performs a logout of the current logged in User
    """

    if env is not None:
        Configuration.override_context(env)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(make_request())

    Configuration.set_token("")
    print_info("You have been logged out.")


async def make_request() -> None:
    async with HttpSession() as session:
        await session.logout()
