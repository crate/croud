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

import json
import unittest
from unittest import mock

import requests
from requests.models import Response

from croud.gql import run_query

me_query = """
{
  me {
    email
    username
    name
  }
}
"""


def _mock_query_response(content: dict, status_code: int) -> Response:
    resp = Response()
    resp.status_code = status_code
    resp._content = bytes(json.dumps(content), encoding="ascii")
    return resp


class TestGql(unittest.TestCase):
    @mock.patch.object(requests, "post")
    def test_successful_query_response(self, mock_requests):
        gql_response = {
            "data": {
                "me": {
                    "email": "sheldon@crate.io",
                    "username": "Google_1234",
                    "name": "Sheldon Cooper",
                }
            }
        }
        mock_requests.return_value = _mock_query_response(gql_response, 200)
        resp = run_query(me_query, "eastus.azure", "dev", "")
        assert resp == gql_response["data"]

    @mock.patch.object(requests, "post")
    @mock.patch("croud.gql.print_error")
    def test_unauthorized_query_response(self, mock_print_error, mock_requests):
        mock_requests.return_value = _mock_query_response("", 200)
        with self.assertRaises(SystemExit) as cm:
            run_query(me_query, "eastus.azure", "dev", "")
        self.assertEqual(cm.exception.code, 1)
        mock_print_error.assert_called_once_with(
            "Unauthorized. Use `croud login` to login to CrateDB Cloud"
        )

    @mock.patch.object(requests, "post")
    @mock.patch("croud.gql.print_error")
    def test_unauthorized_invalid_json_response(self, mock_print_error, mock_requests):
        resp = Response()
        resp.status_code = 200
        resp._content = b"<html></html>"

        mock_requests.return_value = resp
        with self.assertRaises(SystemExit) as cm:
            run_query(me_query, "eastus.azure", "dev", "")
        self.assertEqual(cm.exception.code, 1)
        mock_print_error.assert_called_once_with(
            "Unauthorized. Use `croud login` to login to CrateDB Cloud"
        )

    @mock.patch.object(requests, "post")
    def test_unexpected_response(self, mock_requests):
        resp = Response()
        resp.status_code = 500
        resp._content = b"Server error"

        mock_requests.return_value = resp
        try:
            run_query(me_query, "eastus.azure", "dev", "")
        except Exception as ex:
            self.assertEqual(
                str(ex), f"Query failed to run by returning code of 500. {me_query}"
            )
