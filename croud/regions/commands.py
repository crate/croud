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
from base64 import b64decode

from croud.api import Client
from croud.config import get_output_format
from croud.printer import print_error, print_response, print_success


def regions_list(args: Namespace) -> None:
    """
    Prints the available regions
    """

    client = Client.from_args(args)
    data, errors = client.get("/api/v2/regions/")
    print_response(
        data=data,
        errors=errors,
        keys=["name", "description"],
        output_fmt=get_output_format(args),
    )


def regions_create(args: Namespace) -> None:
    """
    Creates a new region
    """
    client = Client.from_args(args)
    body = {
        "description": args.description,
        "provider": args.provider,
    }

    # Add optional parameters only when present
    if args.name:
        body["name"] = args.name
    if args.org_id:
        body["organization_id"] = args.org_id
    if args.aws_bucket:
        body["aws_bucket"] = args.aws_bucket
    if args.aws_region:
        body["aws_region"] = args.aws_region

    data, errors = client.post("/api/v2/regions/", body=body)

    print_response(
        data=data,
        errors=errors,
        keys=["name", "description"],
        output_fmt=get_output_format(args),
    )


def regions_generate_deployment_manifest(args: Namespace) -> None:
    """
    Returns a manifest file that can be used to setup an edge region in
    a custom kubernetes cluster.
    """

    client = Client.from_args(args)
    data, errors = client.get(
        f"/api/v2/regions/{args.region_name}/deployment-manifest/"
    )
    if data:
        content = b64decode(data["content"]).decode()
        if args.file_name:
            try:
                with open(args.file_name, "x") as file:
                    file.write(content)
                    print_success(f"Manifest written to: {args.file_name}")
            except FileExistsError:
                print_error(f"The file {args.file_name} already exists.")
        else:
            print(content)

    else:
        print_response(
            data=data, errors=errors, output_fmt=get_output_format(args),
        )
