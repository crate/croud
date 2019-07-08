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

import textwrap
from argparse import Namespace

from croud.gql import Query, print_query
from croud.printer import print_warning
from croud.rest import Client
from croud.session import RequestMethod
from croud.util import clean_dict


def roles_add(args: Namespace) -> None:
    """
    Adds a new role to a user
    """

    deprecation_msg = "This command is deprecated."
    if args.role in {"org_admin", "org_member"}:
        deprecation_msg += " Please use `croud organizations users add` instead."
    elif args.role in {"project_admin", "project_member"}:
        deprecation_msg += " Please use `croud projects users add` instead."
    else:
        deprecation_msg += (
            " Please use `croud organizations|projects users add` instead."
        )
    print_warning(deprecation_msg)

    mutation = textwrap.dedent(
        """
        mutation addRoleToUser($input: UserRoleInput!) {
            addRoleToUser(input: $input) {
                success
            }
        }
    """
    ).strip()

    vars = clean_dict(
        {
            "input": {
                "userId": args.user,
                "roleFqn": args.role,
                "resourceId": args.resource,
            }
        }
    )

    query = Query(mutation, args)
    query.execute(vars)
    print_query(query, "addRoleToUser")


def roles_list(args: Namespace) -> None:
    """
    Lists all roles a user can be assigned to
    """

    client = Client.from_args(args)
    client.send(RequestMethod.GET, "/api/v2/roles/")
    client.print(keys=["id", "name"])


def roles_remove(args: Namespace) -> None:
    """
    Removes a role from a user
    """

    deprecation_msg = "This command is deprecated."
    if args.role in {"org_admin", "org_member"}:
        deprecation_msg += " Please use `croud organizations users remove` instead."
    elif args.role in {"project_admin", "project_member"}:
        deprecation_msg += " Please use `croud projects users remove` instead."
    else:
        deprecation_msg += (
            " Please use `croud organizations|projects users remove` instead."
        )
    print_warning(deprecation_msg)

    mutation = textwrap.dedent(
        """
        mutation removeRoleFromUser($input: UserRoleInput!) {
            removeRoleFromUser(input: $input) {
                success
            }
        }
    """
    ).strip()

    vars = clean_dict(
        {
            "input": {
                "userId": args.user,
                "roleFqn": args.role,
                "resourceId": args.resource,
            }
        }
    )

    query = Query(mutation, args)
    query.execute(vars)
    print_query(query, "removeRoleFromUser", "Successfully removed role from user.")
