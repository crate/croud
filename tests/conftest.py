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

from unittest import mock

import pytest
import urllib3

from croud.api import Client

from .util.fake_cloud import FakeCrateDBCloud


@pytest.fixture(scope="session")
def fake_cratedb_cloud():
    with FakeCrateDBCloud() as cloud:
        yield cloud


@pytest.fixture
def client(fake_cratedb_cloud):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    with mock.patch(
        "croud.api.construct_api_base_url",
        return_value=f"https://127.0.0.1:{fake_cratedb_cloud.port}",
    ):
        with mock.patch("croud.api.Configuration.get_token", return_value="some-token"):
            yield Client(env="local", region="bregenz.a1", _verify_ssl=False)
