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
import os
from argparse import Namespace
from typing import Any, Tuple

import bitmath
import requests
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from croud.api import Client
from croud.config import CONFIG, get_output_format
from croud.printer import print_error, print_info, print_response
from croud.tools.spinner import HALO
from croud.util import org_id_config_fallback, require_confirmation


def organizations_create(args: Namespace) -> None:
    client = Client.from_args(args)
    if args.plan_type:
        body = {"name": args.name, "plan_type": args.plan_type}
    else:
        body = {"name": args.name}

    data, errors = client.post("/api/v2/organizations/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "plan_type"],
        success_message="Organization created.",
        output_fmt=get_output_format(args),
    )


@org_id_config_fallback
def organizations_edit(args: Namespace) -> None:
    client = Client.from_args(args)
    body = {}
    if args.plan_type:
        body["plan_type"] = args.plan_type
    if args.name:
        body["name"] = args.name
    if not body:
        print_error("No input arguments found.")
        exit(1)

    data, errors = client.put(f"/api/v2/organizations/{args.org_id}/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "plan_type"],
        success_message="Organization edited.",
        output_fmt=get_output_format(args),
    )


def organizations_get(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/organizations/{args.id}/")
    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
    )


def organizations_list(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get("/api/v2/organizations/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "plan_type"],
        output_fmt=get_output_format(args),
    )


@org_id_config_fallback
@require_confirmation(
    "Are you sure you want to delete the organization?",
    cancel_msg="Organization deletion cancelled.",
)
def organizations_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(f"/api/v2/organizations/{args.org_id}/")
    print_response(
        data=data,
        errors=errors,
        success_message="Organization deleted.",
        output_fmt=get_output_format(args),
    )

    if errors is None and args.org_id == CONFIG.organization:
        CONFIG.set_organization_id(CONFIG.name, None)


def org_files_list(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/organizations/{args.org_id}/files/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "status"],
        output_fmt=get_output_format(args),
    )


def op_upload_file_to_org(
    client, org_id: str, file_path: str, file_name: str = None
) -> Tuple[Any, Any]:
    if not os.path.isfile(file_path):
        return None, {"message": "The file path does not exist."}

    # Name the file in Cloud. If no name is provided the file path will be used.
    payload = {"name": file_name or file_path}
    print_info("Creating a new file upload...")
    data, errors = client.post(f"/api/v2/organizations/{org_id}/files/", body=payload)

    # HALO spinner needs to be stopped to display the progress bar
    HALO.stop()
    if not errors and data and data.get("upload_url"):
        # Progress bar works by wrapping the file and monitoring its read ops
        with tqdm(
            total=os.path.getsize(file_path),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as t:
            with open(file_path, "rb") as file_upload:
                print_info("Uploading the file...")
                wrapped_file = CallbackIOWrapper(t.update, file_upload, "read")
                resp = requests.put(data["upload_url"], data=wrapped_file)
                if resp.status_code < 200 or resp.status_code >= 300:
                    errors = {
                        "code": resp.status_code,
                        "message": "There was an error while trying to upload the file",
                        "upload_url": data["upload_url"],
                    }

    return data, errors


def org_files_create(args: Namespace) -> None:
    client = Client.from_args(args)

    data, errors = op_upload_file_to_org(client, args.org_id, args.file_path, args.name)
    if errors or not data:
        print_response(
            data=data,
            errors=errors,
            success_message="There was a problem uploading the file.",
            keys=["id", "name", "status"],
            output_fmt=get_output_format(args),
        )
    else:
        # Refresh the data from the file resource to get the latest status.
        data_refresh, errors = client.get(f"/api/v2/organizations/{args.org_id}/files/")
        if data_refresh:
            file = [x for x in data_refresh if x["id"] == data["id"]]
        print_response(
            data=file,
            errors=errors,
            success_message="File upload completed!",
            keys=["id", "name", "status"],
            output_fmt=get_output_format(args),
        )


def org_files_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(
        f"/api/v2/organizations/{args.org_id}/files/{args.file_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        success_message="File upload deleted.",
        output_fmt=get_output_format(args),
    )


def org_files_get(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(
        f"/api/v2/organizations/{args.org_id}/files/{args.file_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "status", "file_size", "download_url"],
        output_fmt=get_output_format(args),
        transforms={
            "file_size": _transform_file_size,
        },
    )


def _transform_file_size(size_bytes):
    if not size_bytes:
        return None
    return bitmath.Byte(size_bytes).best_prefix().format("{value:.2f} {unit}")
