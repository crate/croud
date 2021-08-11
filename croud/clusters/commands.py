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
from croud.printer import print_response
from croud.util import require_confirmation


def clusters_get(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/clusters/{args.id}/")
    print_response(
        data=data, errors=errors, output_fmt=get_output_format(args),
    )


def clusters_list(args: Namespace) -> None:
    params = {}
    if args.project_id:
        params["project_id"] = args.project_id

    client = Client.from_args(args)
    data, errors = client.get("/api/v2/clusters/", params=params)
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
    _handle_edge_params(body, args)
    client = Client.from_args(args)
    data, errors = client.post("/api/v2/clusters/", body=body)
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
    body = {"product_unit": args.unit}
    client = Client.from_args(args)
    data, errors = client.put(f"/api/v2/clusters/{args.cluster_id}/scale/", body=body)
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
    body = {"crate_version": args.version}
    client = Client.from_args(args)
    data, errors = client.put(f"/api/v2/clusters/{args.cluster_id}/upgrade/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "crate_version"],
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
    data, errors = client.delete(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        success_message="Cluster deleted.",
        output_fmt=get_output_format(args),
    )


def clusters_restart_node(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(
        f"/api/v2/clusters/{args.cluster_id}/nodes/{args.ordinal}"
    )
    print_response(
        data=data,
        errors=errors,
        keys=["code", "status"],
        success_message=(
            "Node restarted. It may take a few minutes to complete the changes."
        ),
        output_fmt=get_output_format(args),
    )


def clusters_set_deletion_protection(args: Namespace) -> None:
    body = {"deletion_protected": args.value}
    client = Client.from_args(args)
    data, errors = client.put(
        f"/api/v2/clusters/{args.cluster_id}/deletion-protection/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "deletion_protected"],
        success_message=("Cluster deletion protection status successfully updated"),
        output_fmt=get_output_format(args),
    )


# We want to map the custom hardware specs to slightly nicer params in croud,
# hence this mapping here
def _handle_edge_params(body, args):
    if args.cpus:
        body.setdefault("hardware_specs", {})["cpus_per_node"] = args.cpus
    if args.disks:
        body.setdefault("hardware_specs", {})["disks_per_node"] = args.disks
    if args.disk_size_gb:
        body.setdefault("hardware_specs", {})["disk_size_per_node_bytes"] = (
            args.disk_size_gb * 1024 * 1024 * 1024
        )
    if args.disk_type:
        body.setdefault("hardware_specs", {})["disk_type"] = args.disk_type
    if args.memory_size_mb:
        body.setdefault("hardware_specs", {})["memory_per_node_bytes"] = (
            args.memory_size_mb * 1024 * 1024
        )
