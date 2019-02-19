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
from textwrap import dedent

from croud.gql import Query, print_query
from croud.util import clean_dict


def consumer_sets_list(args: Namespace) -> None:
    body = dedent(
        """
    query allConsumerSets($clusterId: String, $productId: String, $projectId: String) {
        allConsumerSets(clusterId: $clusterId, productId: $productId, projectId: $projectId) {
            id
            name
            projectId
            instances
            config {
                cluster {
                    id
                    schema
                    table
                }
                consumerGroup
                leaseStorageContainer
            }
        }
    }
    """  # noqa
    ).strip()

    vars = clean_dict(
        {
            "projectId": args.project_id,
            "productId": args.product_id,
            "clusterId": args.cluster_id,
        }
    )

    query = Query(body, args, endpoint="/product/graphql")
    query.execute(vars)
    print_query(query, "allConsumerSets")


def consumer_sets_edit(args: Namespace) -> None:
    body = dedent(
        """
    mutation editConsumerSet($id: String!, $input: EditConsumerSetInput!) {
        editConsumerSet(
            id: $id,
            input: $input
        ) {
            id
        }
    }
    """  # noqa
    ).strip()

    vars = clean_dict(
        {
            "id": args.consumer_set_id,
            "input": {
                "eventhub": {
                    "connectionString": args.consumer_eventhub_connection_string,
                    "consumerGroup": args.consumer_eventhub_consumer_group,
                    "leaseStorage": {
                        "connectionString": args.consumer_eventhub_lease_storage_connection_string,  # noqa
                        "container": args.consumer_eventhub_lease_storage_container,
                    },
                },
                "cluster": {
                    "schema": args.consumer_schema,
                    "table": args.consumer_table,
                },
            },
        }
    )

    query = Query(body, args, endpoint="/product/graphql")
    query.execute(vars)
    print_query(query, "editConsumerSet")
