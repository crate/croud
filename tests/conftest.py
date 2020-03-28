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

import secrets
from unittest import mock

import pytest
import urllib3

import croud.config
from croud.api import Client
from croud.config.configuration import Configuration
from tests.util.fake_cloud import FakeCrateDBCloud

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope="session")
def fake_cratedb_cloud():
    with FakeCrateDBCloud() as cloud:
        yield cloud


@pytest.fixture
def config(fake_cratedb_cloud, tmp_path):
    profile = secrets.token_urlsafe(16)

    config = Configuration("croud.yaml", tmp_path)
    config.add_profile(profile, endpoint=f"https://127.0.0.1:{fake_cratedb_cloud.port}")
    config.set_auth_token(profile, secrets.token_urlsafe(64))
    config.use_profile(profile)

    with mock.patch.object(croud.config, "_CONFIG", config):
        yield config


@pytest.fixture
def client(fake_cratedb_cloud, config):
    yield Client(
        config.endpoint,
        token=config.token,
        on_token=config.set_current_auth_token,
        region="bregenz.a1",
        _verify_ssl=False,
    )
