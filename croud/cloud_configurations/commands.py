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


def _org_id_transform(field):
    return field or ""


def cloud_configurations_set(args: Namespace) -> None:
    body = {"value": args.value}
    if args.org_id:
        body["organization_id"] = args.org_id

    client = Client.from_args(args)
    data, errors = client.put(f"/api/v2/configurations/{args.key}/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["key", "value", "organization_id"],
        success_message="Configuration updated.",
        output_fmt=get_output_format(args),
        transforms={"organization_id": _org_id_transform},
    )


def cloud_configurations_get(args: Namespace) -> None:
    client = Client.from_args(args)
    params = {}
    if args.org_id:
        params["organization_id"] = args.org_id
    data, errors = client.get(f"/api/v2/configurations/{args.key}/", params=params)
    print_response(
        data=data,
        errors=errors,
        keys=["key", "value", "organization_id"],
        output_fmt=get_output_format(args),
        transforms={"organization_id": _org_id_transform},
    )


def cloud_configurations_list(args: Namespace) -> None:
    client = Client.from_args(args)
    params = {}
    if args.org_id:
        params["organization_id"] = args.org_id
    data, errors = client.get("/api/v2/configurations/", params=params)
    print_response(
        data=data,
        errors=errors,
        keys=["key", "value", "organization_id"],
        output_fmt=get_output_format(args),
        transforms={"organization_id": _org_id_transform},
    )
