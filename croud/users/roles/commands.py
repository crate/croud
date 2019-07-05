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

from croud.organizations.users.commands import org_users_add, org_users_remove
from croud.printer import print_error
from croud.projects.users.commands import project_users_add, project_users_remove
from croud.rest import Client
from croud.session import RequestMethod


def roles_add(args: Namespace) -> None:
    """
    Adds a new role to a user
    """
    if args.role in {"org_admin", "org_member"}:
        args.org_id = args.resource
        org_users_add(args)
    elif args.role in {"project_admin", "project_member"}:
        args.project_id = args.resource
        project_users_add(args)
    else:
        print_error(f"Invalid role '{args.role}'.")


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
    if args.role in {"org_admin", "org_member"}:
        args.org_id = args.resource
        org_users_remove(args)
    elif args.role in {"project_admin", "project_member"}:
        args.project_id = args.resource
        project_users_remove(args)
    else:
        print_error(f"Invalid role '{args.role}'.")
