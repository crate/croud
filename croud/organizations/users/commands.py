#!/usr/bin/env python
#
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

from croud.rest import Client
from croud.session import RequestMethod
from croud.util import require_confirmation


def org_users_add(args: Namespace):
    body = {"user_id": args.user, "role_fqn": args.role}
    client = Client(env=args.env, region=args.region)
    client.send(
        RequestMethod.POST, f"/api/v2/organizations/{args.org_id}/users/", body=body
    )
    client.print(keys=["user_id", "organization_id", "role_fqn"])


@require_confirmation(
    "Are you sure you want to remove the user?",
    cancel_msg="Removing user cancelled.",
)
def org_users_remove(args: Namespace):
    client = Client(env=args.env, region=args.region)
    client.send(
        RequestMethod.DELETE, f"/api/v2/organizations/{args.org_id}/users/{args.user}/"
    )
    client.print(
        f"The user with the id {args.user} was successfully removed from the org {args.org_id}"
    )
