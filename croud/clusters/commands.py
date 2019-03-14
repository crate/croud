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


def clusters_list(args: Namespace) -> None:
    """
    Lists all projects for the current user in the specified region
    """

    body = textwrap.dedent(
        """
        query allClusters($filter: [ClusterFilter]) {
            allClusters(sort: [CRATE_VERSION_DESC], filter: $filter) {
                data {
                    id
                    name
                    numNodes
                    crateVersion
                    projectId
                    username
                    fqdn
                }
            }
        }
    """
    ).strip()

    project_filter = (
        {"by": "PROJECT_ID", "op": "EQ", "value": args.project_id}
        if args.project_id
        else None
    )
    vars = clean_dict({"filter": [project_filter] if project_filter else None})

    query = Query(body, args)
    query.execute(vars)
    print_query(query, "allClusters")


def clusters_deploy(args: Namespace) -> None:
    """
    Deploys a new cluster CrateDB cluster.
    """

    mutation = textwrap.dedent(
        """
        mutation deployCluster($input: DeployClusterInput!) {
            deployCluster(input: $input) {
                id
                name
                fqdn
                url
            }
        }
    """  # noqa
    ).strip()

    vars = clean_dict(
        {
            "input": {
                "productName": args.product_name,
                "tier": args.tier,
                "unit": args.unit,
                "name": args.cluster_name,
                "projectId": args.project_id,
                "username": args.username,
                "password": args.password,
                "version": args.version,
            }
        }
    )

    query = Query(mutation, args)
    query.execute(vars)
    print_query(query, "deployCluster")
