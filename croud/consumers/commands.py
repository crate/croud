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
from croud.rest import Client
from croud.session import RequestMethod
from croud.util import clean_dict


def consumers_deploy(args: Namespace) -> None:
    body = dedent(
        """
    mutation deployConsumer($input: DeployConsumerInput!) {
        deployConsumer(input: $input) {
            id
            name
            projectId
            clusterId
            productName
            productTier
            instances
            tableName
            tableSchema
        }
    }
    """  # noqa
    ).strip()

    vars = clean_dict(
        {
            "input": {
                "name": args.consumer_name,
                "productName": args.product_name,
                "productTier": args.tier,
                "tableName": args.consumer_table,
                "tableSchema": args.consumer_schema,
                "clusterId": args.cluster_id,
                "projectId": args.project_id,
                "instances": args.num_instances,
                "eventhubConnectionString": args.eventhub_dsn,
                "eventhubConsumerGroup": args.eventhub_consumer_group,
                "leaseStorageContainer": args.lease_storage_container,
                "leaseStorageConnectionString": args.lease_storage_dsn,
            }
        }
    )

    query = Query(body, args)
    query.execute(vars)
    print_query(query, "deployConsumer")


def consumers_list(args: Namespace) -> None:
    params = {}
    if args.cluster_id:
        params["cluster_id"] = args.cluster_id
    if args.product_name:
        params["product_name"] = args.product_name
    if args.project_id:
        params["project_id"] = args.project_id

    client = Client(env=args.env, output_fmt=args.output_fmt)
    client.send(RequestMethod.GET, "/api/v2/consumers/", params=params)
    client.print(
        keys=[
            "cluster_id",
            "id",
            "instances",
            "name",
            "product_name",
            "product_tier",
            "project_id",
            "table_name",
            "table_schema",
        ]
    )


def consumers_edit(args: Namespace) -> None:
    body = dedent(
        """
    mutation editConsumer($id: String!, $input: EditConsumerInput!) {
        editConsumer(id: $id, input: $input) {
            id
        }
    }
    """  # noqa
    ).strip()

    vars = clean_dict(
        {
            "id": args.consumer_id,
            "input": {
                "eventhubConnectionString": args.eventhub_dsn,
                "eventhubConsumerGroup": args.eventhub_consumer_group,
                "leaseStorageConnectionString": args.lease_storage_dsn,
                "leaseStorageContainer": args.lease_storage_container,
                "consumerSchema": args.consumer_schema,
                "consumerTable": args.consumer_table,
                "clusterId": args.cluster_id,
            },
        }
    )

    query = Query(body, args)
    query.execute(vars)
    print_query(query, "editConsumer")
