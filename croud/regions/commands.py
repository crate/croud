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
from croud.printer import print_error, print_raw, print_response, print_success
from croud.util import require_confirmation


def regions_list(args: Namespace) -> None:
    """
    Prints the available regions
    """

    client = Client.from_args(args)
    if args.org_id:
        url = f"/api/v2/organizations/{args.org_id}/regions/"
    else:
        url = "/api/v2/regions/"
    data, errors = client.get(url)
    print_response(
        data=data,
        errors=errors,
        keys=["name", "description", "organization_id"],
        output_fmt=get_output_format(args),
        transforms={"organization_id": _organization_id_transform},
    )


@require_confirmation(
    "Creating a region is an experimental feature. Are you sure you want to proceed?",  # noqa
    cancel_msg="Region creation cancelled.",
)
def regions_create(args: Namespace) -> None:
    """
    Creates a new region
    """
    client = Client.from_args(args)
    body = {"description": args.description, "organization_id": args.org_id}

    # Add optional parameters only when present
    if args.aws_bucket:
        body["aws_bucket"] = args.aws_bucket
    if args.aws_region:
        body["aws_region"] = args.aws_region

    region, region_errors = client.post("/api/v2/regions/", body=body)

    print_response(
        data=region,
        errors=region_errors,
        keys=["name", "description"],
        output_fmt=get_output_format(args),
    )

    if not region_errors and region and "name" in region:
        install_token, install_token_errors = client.get(
            f"/api/v2/regions/{region['name']}/install-token/"
        )

        if not install_token_errors and install_token and "token" in install_token:
            print_success("You have successfully created a region.")

            print_raw(
                [
                    "",
                    "To install the edge region run the following command:",
                    "",
                    f"  $ bash <( wget -qO- {client.base_url}/edge/cratedb-cloud-edge.sh) {install_token['token']}",  # noqa
                    "",
                ],
            )
        else:
            print_response(
                data=install_token,
                errors=install_token_errors,
                keys=["token"],
                output_fmt=get_output_format(args),
            )


@require_confirmation(
    "Deleting a region is an experimental feature. Are you sure you want to proceed?",  # noqa
    cancel_msg="Region deletion cancelled.",
)
def regions_delete(args: Namespace) -> None:
    """
    Deletes a new region
    """
    client = Client.from_args(args)
    region_name = args.name

    regions, errors = client.get("/api/v2/regions/")
    region = next((r for r in (regions or []) if r["name"] == region_name), None)

    if not region:
        print_error(f"The region {region_name} does not exist.")
        return

    # Check edge region status
    if region["is_edge_region"] and region["status"] == "UP":
        print_response(
            data=region,
            errors={
                "message": (
                    "Your region is still connected to CrateDB Cloud. Please uninstall "
                    "the CrateDB Edge stack from the region before deleting it by "
                    "running the script below:\nbash <(wget -qO- "
                    f"{client.base_url}/edge/uninstall-cratedb-cloud-edge.sh)"
                ),
                "errors": {},
            },
            output_fmt=get_output_format(args),
        )
        return

    data, region_errors = client.delete(f"/api/v2/regions/{region_name}/")

    if region_errors:
        print_response(
            data=data,
            errors={
                "message": region_errors.get("message"),
                "errors": {"related_resources": region_errors.get("related_resources")},
            },
            output_fmt=get_output_format(args),
        )
    else:
        print_response(
            data=data,
            errors=region_errors,
            success_message="You have successfully deleted a region.",
            output_fmt=get_output_format(args),
        )


def _organization_id_transform(field):
    return field if field else ""
