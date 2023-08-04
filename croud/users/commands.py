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
from croud.printer import print_response, print_warning
from croud.util import require_confirmation


def transform_roles_list(key):
    def _transform(field):
        return ",\n".join(f"{r[key]}: {r['role_fqn']}" for r in field)

    return _transform


def users_list(args: Namespace) -> None:
    client = Client.from_args(args)
    if args.no_org:
        print_warning(
            "The --no-org argument is deprecated. Please use --no-roles instead."
        )

    no_roles = {"no-roles": "1"} if (args.no_roles or args.no_org) else None
    data, errors = client.get("/api/v2/users/", params=no_roles)
    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
        keys=["uid", "email", "username", "organization_roles", "project_roles"],
        transforms={
            "organization_roles": transform_roles_list("organization_id"),
            "project_roles": transform_roles_list("project_id"),
        },
    )


@require_confirmation(
    "Are you sure you want to delete the user?",
    cancel_msg="User deletion cancelled.",
)
def users_delete(args: Namespace) -> None:
    client = Client.from_args(args)

    data, errors = client.delete(f"/api/v2/users/{args.user_id}/")
    print_response(
        data=data,
        errors=errors,
        success_message="User deleted.",
        output_fmt=get_output_format(args),
    )
