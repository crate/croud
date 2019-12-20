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


import pytest
import requests

from croud.server import Server


@pytest.mark.parametrize(
    "qs,status_code,message,token_value",
    [
        ("?token=foo", 200, "You have successfully logged into CrateDB Cloud!", "foo"),
        ("", 400, "Authentication token missing in URL.", None),
        (
            "?token=foo&token=bar",
            400,
            "ore than one authentication token present in URL.",
            None,
        ),
    ],
)
def test_token_handler_and_login(qs, status_code, message, token_value):
    token_store = {}

    def on_token(token):
        token_store["token"] = token

    server = Server(on_token, random_port=True).start_in_background()

    response = requests.get(f"http://localhost:{server.port}/{qs}")

    if token_value is not None:
        assert token_store["token"] == token_value
    else:
        assert "token" not in token_store
    assert response.status_code == status_code
    assert message in response.text
