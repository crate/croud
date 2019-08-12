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

from croud.config import Configuration
from croud.printer import print_info
from croud.transport import Client, cloud_url, session_logout

LOGOUT_PATH = "/oauth2/logout"


def logout(args: Namespace) -> None:
    env = args.env or Configuration.get_env()
    region = args.region or Configuration.get_setting("region")

    make_request(env, region)
    Configuration.set_token("", env)
    Configuration.set_organization_id("", env)

    print_info("You have been logged out.")


def make_request(env: str, region: str) -> None:
    client_session = Client(env=env, region=region)
    with client_session._session as session:
        session.cookies.clear()
        session_logout(session, _logout_url(env))


def _logout_url(env: str) -> str:
    return cloud_url(env) + LOGOUT_PATH
