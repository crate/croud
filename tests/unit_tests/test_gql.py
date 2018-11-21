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
import unittest
from unittest import mock

import aiohttp
from util.fake_server import FakeCrateDBCloud, FakeResolver

from croud.config import Configuration
from croud.gql import _query

me_query = """
{
  me {
    email
    username
    name
  }
}
"""

me_response = {
    "me": {
        "email": "sheldon@crate.io",
        "username": "Google_1234",
        "name": "Sheldon Cooper",
    }
}


class TestGql(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.fake_cloud = FakeCrateDBCloud(loop=self.loop)
        info = self.loop.run_until_complete(self.fake_cloud.start())
        resolver = FakeResolver(info, loop=self.loop)
        self.connector = aiohttp.TCPConnector(
            loop=self.loop, resolver=resolver, ssl=True
        )

    def tearDown(self):
        self.loop.run_until_complete(self.fake_cloud.stop())

    @mock.patch.object(Configuration, "read_token", return_value="eyJraWQiOiIx")
    def test_query_success(self, mock_token):
        async def test_query():
            result = await _query(
                "https://cratedb.cloud/graphql", me_query, self.connector, headers
            )
            self.assertEqual(result, me_response)

        # testing-only: tell the graphql endpoint which query is tested
        headers = {"query": "me"}
        self.loop.run_until_complete(test_query())

    @mock.patch.object(Configuration, "read_token", return_value="")
    @mock.patch("croud.gql.print_error")
    def test_query_unauthorized(self, mock_print_error, mock_token):
        async def test_query():
            with self.assertRaises(SystemExit) as cm:
                await _query(
                    "https://cratedb.cloud/graphql", me_query, self.connector, headers
                )
            mock_print_error.assert_called_once_with(
                "Unauthorized. Use `croud login` to login to CrateDB Cloud."
            )
            self.assertEqual(cm.exception.code, 1)

        # testing-only: tell the graphql endpoint which query is tested
        headers = {"query": "me"}
        self.loop.run_until_complete(test_query())
