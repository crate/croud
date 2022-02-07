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
from croud.printer import print_error, print_response
from croud.util import org_id_config_fallback, require_confirmation


@org_id_config_fallback
def project_create(args: Namespace) -> None:
    body = {"name": args.name, "organization_id": args.org_id}
    _handle_custom_backups(body, args)
    client = Client.from_args(args)
    data, errors = client.post("/api/v2/projects/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id"],
        success_message="Project created.",
        output_fmt=get_output_format(args),
    )


@require_confirmation(
    "Are you sure you want to delete the project?",
    cancel_msg="Project deletion cancelled.",
)
def project_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(f"/api/v2/projects/{args.project_id}/")
    print_response(
        data=data,
        errors=errors,
        success_message="Project deleted.",
        output_fmt=get_output_format(args),
    )


def project_edit(args: Namespace) -> None:
    client = Client.from_args(args)
    body = {}
    if args.name:
        body["name"] = args.name
    if not body:
        print_error("No input arguments found.")
        exit(1)

    data, errors = client.patch(f"/api/v2/projects/{args.project_id}/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name"],
        success_message="Project edited.",
        output_fmt=get_output_format(args),
    )


def projects_get(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/projects/{args.id}/")
    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
        transforms={"backup_location": _transform_backup_location},
    )


def projects_list(args: Namespace) -> None:
    client = Client.from_args(args)
    if args.org_id:
        url = f"/api/v2/organizations/{args.org_id}/projects/"
    else:
        url = "/api/v2/projects/"
    data, errors = client.get(url)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "region", "organization_id", "backup_location"],
        transforms={"backup_location": _transform_backup_location},
        output_fmt=get_output_format(args),
    )


def _handle_custom_backups(body, args: Namespace) -> None:
    if args.backup_location_type:
        body.setdefault("backup_location", {})[
            "location_type"
        ] = args.backup_location_type
    if args.backup_location:
        body.setdefault("backup_location", {})["location"] = args.backup_location
    if args.backup_location_access_key_id and args.backup_location_secret_access_key:
        body.setdefault("backup_location", {})["credentials"] = {
            "access_key_id": args.backup_location_access_key_id,
            "secret_access_key": args.backup_location_secret_access_key,
        }
    if args.backup_location_endpoint_url:
        body.setdefault("backup_location", {})["additional_config"] = {
            "endpoint_url": args.backup_location_endpoint_url,
        }


def _transform_backup_location(field):
    if not field:
        return "default"

    return f"{field['location_type']}://{field['location']}"
