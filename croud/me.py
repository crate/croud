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

import argh

from croud.gql import run_query
from croud.printer import print_format


@argh.arg(
    "-r",
    "--region",
    choices=["westeurope.azure", "eastus.azure", "bregenz.a1"],
    default="bregenz.a1",
    type=str,
)
@argh.arg("--env", choices=["dev", "prod"], default="prod", type=str)
@argh.arg("-o", "--output-fmt", choices=["json"], default="json", type=str)
def me(region=None, env=None, output_fmt=None) -> None:
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

    resp = run_query(query, region, env)
    print_format(resp["me"], output_fmt)
