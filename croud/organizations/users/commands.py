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


import textwrap
from argparse import Namespace

from croud.gql import Query, print_query


def org_users_add(args: Namespace):
    mutation = textwrap.dedent(
        """
        mutation addUserToOrganization($input: AddUserToOrganizationInput!) {
          addUserToOrganization(input: $input) {
            user {
              uid
              email
              organizationId
            }
          }
        }
    """
    ).strip()

    vars = {"input": {"user": args.user, "organizationId": args.org_id}}
    if args.role is not None:
        vars["input"]["roleFqn"] = args.role

    query = Query(mutation, args)
    query.execute(vars)
    print_query(query, "addUserToOrganization")


def org_users_remove(args: Namespace):
    mutation = textwrap.dedent(
        """
        mutation removeUserFromOrganization($input: RemoveUserFromOrganizationInput!) {
          removeUserFromOrganization(input: $input) {
            success
          }
        }
    """
    ).strip()

    vars = {"input": {"user": args.user, "organizationId": args.org_id}}

    query = Query(mutation, args)
    query.execute(vars)
    print_query(query, "removeUserFromOrganization")
