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


def clusters_list(args: Namespace) -> None:
    """
    Lists all projects for the current user in the specified region
    """

    params = {}
    if args.project_id:
        params["project_id"] = args.project_id

    client = Client.from_args(args)
    data, errors = client.send(RequestMethod.GET, "/api/v2/clusters/", params=params)
    print_response(
        data=data,
        errors=errors,
        keys=[
            "id",
            "name",
            "num_nodes",
            "crate_version",
            "project_id",
            "username",
            "fqdn",
            "channel",
        ],
        output_fmt=get_output_format(args),
    )


def clusters_deploy(args: Namespace) -> None:
    """
    Deploys a new CrateDB cluster.
    """

    body = {
        "crate_version": args.version,
        "name": args.cluster_name,
        "password": args.password,
        "product_name": args.product_name,
        "product_tier": args.tier,
        "project_id": args.project_id,
        "username": args.username,
        "channel": args.channel,
    }
    if args.unit:
        body["product_unit"] = args.unit
    client = Client.from_args(args)
    data, errors = client.send(RequestMethod.POST, "/api/v2/clusters/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "fqdn", "url"],
        success_message=(
            "Cluster deployed. It may take a few minutes to complete the changes."
        ),
        output_fmt=get_output_format(args),
    )


def clusters_scale(args: Namespace) -> None:
    """
    Scale an existing CrateDB cluster.
    """

    body = {"product_unit": args.unit}
    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.PUT, f"/api/v2/clusters/{args.cluster_id}/scale/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "num_nodes"],
        success_message=(
            "Cluster scaled. It may take a few minutes to complete the changes."
        ),
        output_fmt=get_output_format(args),
    )


def clusters_upgrade(args: Namespace) -> None:
    """
    Upgrade an existing CrateDB Cluster to a later version.
    """

    body = {"crate_version": args.version}
    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.PUT, f"/api/v2/clusters/{args.cluster_id}/upgrade/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "num_nodes"],
        success_message=(
            "Cluster upgraded. It may take a few minutes to complete the changes."
        ),
        output_fmt=get_output_format(args),
    )


@require_confirmation(
    "Are you sure you want to delete the cluster?",
    cancel_msg="Cluster deletion cancelled.",
)
def clusters_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.DELETE, f"/api/v2/clusters/{args.cluster_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        success_message="Cluster deleted.",
        output_fmt=get_output_format(args),
    )
