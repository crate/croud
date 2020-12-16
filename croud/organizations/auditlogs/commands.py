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

import re
from argparse import Namespace
from typing import Dict, List

from croud.api import Client
from croud.config import get_output_format
from croud.printer import print_error, print_response
from croud.util import org_id_config_fallback

# Hat tip to Django for ISO8601 deserialization functions

iso8601_datetime_re = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})"
    r"(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?"
    r"(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$"
)


def actor_id_transform(field):
    return field["id"] or "SYSTEM"


@org_id_config_fallback
def auditlogs_list(args: Namespace) -> None:
    client = Client.from_args(args)
    url = f"/api/v2/organizations/{args.org_id}/auditlogs/"
    data: List[Dict] = []
    cursor = None

    params = {}
    if args.action:
        params["action"] = args.action

    if args.from_:
        if not iso8601_datetime_re.fullmatch(args.from_):
            print_error("Invalid 'from' date format.")
        params["from"] = args.from_

    if args.to:
        if not iso8601_datetime_re.fullmatch(args.to):
            print_error("Invalid 'to' date format.")
        params["to"] = args.to

    while True:
        if cursor:
            params["last"] = cursor
        page, errors = client.get(url, params=params)
        if errors or not page:
            break
        else:
            data.extend(page)
            cursor = data[-1]["id"]

    print_response(
        data=data,
        errors=errors,
        keys=["action", "actor", "created"],
        output_fmt=get_output_format(args),
        transforms={"actor": actor_id_transform},
    )
