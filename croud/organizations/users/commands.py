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

from croud.api import Client
from croud.config import get_output_format
from croud.printer import print_response
from croud.util import org_id_config_fallback


@org_id_config_fallback
def org_users_add(args: Namespace):
    client = Client.from_args(args)
    data, errors = client.post(
        f"/api/v2/organizations/{args.org_id}/users/",
        body={"user": args.user, "role_fqn": args.role},
    )
    if data is not None and data.get("added", False):
        success_message = "User added to organization."
    else:
        success_message = "Role altered for user."

    print_response(
        data=data,
        errors=errors,
        keys=["user_id", "organization_id", "role_fqn"],
        success_message=success_message,
        output_fmt=get_output_format(args),
    )


def role_fqn_transform(field):
    return field[0]["role_fqn"]


@org_id_config_fallback
def org_users_list(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/organizations/{args.org_id}/users/")
    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
        keys=["uid", "email", "username", "organization_roles"],
        transforms={"organization_roles": role_fqn_transform},
    )


@org_id_config_fallback
def org_users_remove(args: Namespace):
    client = Client.from_args(args)
    data, errors = client.delete(
        f"/api/v2/organizations/{args.org_id}/users/{args.user}/"
    )
    print_response(
        data=data,
        errors=errors,
        success_message="User removed from organization.",
        output_fmt=get_output_format(args),
    )
