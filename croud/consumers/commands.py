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

from croud.config import get_output_format
from croud.printer import print_response
from croud.rest import Client
from croud.session import RequestMethod
from croud.util import require_confirmation


def consumers_deploy(args: Namespace) -> None:
    body = {
        "cluster_id": args.cluster_id,
        "config": {
            "connection_string": args.eventhub_dsn,
            "consumer_group": args.eventhub_consumer_group,
            "consumer_lease_container": args.lease_storage_container,
            "lease_storage_connection_string": args.lease_storage_dsn,
        },
        "instances": args.num_instances,
        "name": args.consumer_name,
        "product_name": args.product_name,
        "product_tier": args.tier,
        "project_id": args.project_id,
        "table_name": args.consumer_table,
        "table_schema": args.consumer_schema,
    }
    client = Client.from_args(args)
    data, errors = client.send(RequestMethod.POST, "/api/v2/consumers/", body=body)
    print_response(
        data=data,
        errors=errors,
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
        ],
        success_message=(
            "Consumer deployed. It may take a few minutes to complete the changes."
        ),
        output_fmt=get_output_format(args),
    )


def consumers_list(args: Namespace) -> None:
    params = {}
    if args.cluster_id:
        params["cluster_id"] = args.cluster_id
    if args.product_name:
        params["product_name"] = args.product_name
    if args.project_id:
        params["project_id"] = args.project_id

    client = Client.from_args(args)
    data, errors = client.send(RequestMethod.GET, "/api/v2/consumers/", params=params)
    print_response(
        data=data,
        errors=errors,
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
        ],
        output_fmt=get_output_format(args),
    )


def consumers_edit(args: Namespace) -> None:
    body = {
        "cluster_id": args.cluster_id,
        "table_name": args.consumer_table,
        "table_schema": args.consumer_schema,
    }
    config = {}
    if args.eventhub_dsn:
        config["connection_string"] = args.eventhub_dsn
    if args.eventhub_consumer_group:
        config["consumer_group"] = args.eventhub_consumer_group
    if args.lease_storage_container:
        config["consumer_lease_container"] = args.lease_storage_container
    if args.lease_storage_dsn:
        config["lease_storage_connection_string"] = args.lease_storage_dsn

    if config:
        body["config"] = config
    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.PATCH, f"/api/v2/consumers/{args.consumer_id}/", body=body
    )
    print_response(
        data=data, errors=errors, keys=["id"], output_fmt=get_output_format(args)
    )


@require_confirmation(
    "Are you sure you want to delete the consumer?",
    cancel_msg="Consumer deletion cancelled.",
)
def consumers_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.DELETE, f"/api/v2/consumers/{args.consumer_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        success_message="Consumer deleted.",
        output_fmt=get_output_format(args),
    )
