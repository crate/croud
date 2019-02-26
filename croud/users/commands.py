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
from croud.util import clean_dict


def users_list(args: Namespace) -> None:
    """
    List all users within organizations that the logged in user is part of
    """

    body = textwrap.dedent(
        """
        query allUsers($queryArgs: UserQueryArgs) {
            allUsers(sort: EMAIL, queryArgs: $queryArgs) {
                data {
                    uid
                    email
                    username
                }
            }
        }
    """
    ).strip()

    vars = clean_dict(
        {"queryArgs": {"noOrg": args.no_org, "organizationId": args.org_id}}
    )

    query = Query(body, args)
    query.execute(vars)
    print_query(query, "allUsers")
