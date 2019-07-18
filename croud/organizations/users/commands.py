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


def org_users_add(args: Namespace):
    client = Client.from_args(args)

    client.send(
        RequestMethod.POST,
        f"/api/v2/organizations/{args.org_id}/users/",
        body={"user": args.user, "role_fqn": args.role},
    )
    if "@" in args.user:
        client.print(success_message=f"User with mail {args.user} was added.")
    else:
        client.print(success_message=f"User with id {args.user} was added.")


def org_users_remove(args: Namespace):
    client = Client.from_args(args)

    client.send(
        RequestMethod.DELETE, f"/api/v2/organizations/{args.org_id}/users/{args.user}/"
    )
    client.print(success_message="User removed from organization.")
