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
from typing import List, Union

import argh

from croud.printer import print_error, print_format
from croud.session import HttpSession
from croud.typing import JsonDict


@argh.arg(
    "-r",
    "--region",
    choices=["westeurope.azure", "eastus.azure", "bregenz.a1"],
    default="bregenz.a1",
    type=str,
)
@argh.arg("-o", "--output-fmt", choices=["json", "table"], default="json", type=str)
def me(region=None, output_fmt=None) -> None:
    """
    Prints the current logged in user
    """
    # Todo: Return the current logged in user
    query = """
{
    me {
        email
        username
        name
    }
}
    """

    async def fetch_data() -> Union[List[JsonDict], JsonDict]:
        async with HttpSession(region) as session:
            return await session.fetch(query)

    loop = asyncio.get_event_loop()
    rows = loop.run_until_complete(fetch_data())

    if rows:
        if isinstance(rows, dict):
            print_format(rows["me"], output_fmt)
        else:
            print_error("Result has no proper format to print.")
    else:
        print_error("Result contained no data to print.")
