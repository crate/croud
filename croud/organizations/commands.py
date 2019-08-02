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

from croud.config import Configuration, get_output_format
from croud.printer import print_error, print_response
from croud.rest import Client
from croud.session import RequestMethod
from croud.util import org_id_config_fallback, require_confirmation


def organizations_create(args: Namespace) -> None:
    """
    Creates an organization
    """

    client = Client.from_args(args)
    if args.plan_type:
        body = {"name": args.name, "plan_type": args.plan_type}
    else:
        body = {"name": args.name}

    data, errors = client.send(RequestMethod.POST, "/api/v2/organizations/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "plan_type"],
        success_message="Organization created.",
        output_fmt=get_output_format(args),
    )


@org_id_config_fallback
def organizations_edit(args: Namespace) -> None:
    """
    Edit an organization
    """

    client = Client.from_args(args)
    body = {}
    if args.plan_type:
        body["plan_type"] = args.plan_type
    if args.name:
        body["name"] = args.name
    if not body:
        print_error("No input arguments found.")
        exit(1)

    data, errors = client.send(
        RequestMethod.PUT, f"/api/v2/organizations/{args.org_id}/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "plan_type"],
        success_message="Organization edited.",
        output_fmt=get_output_format(args),
    )


def organizations_list(args: Namespace) -> None:
    """
    Lists organizations
    """

    client = Client.from_args(args)
    data, errors = client.send(RequestMethod.GET, "/api/v2/organizations/")
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
    """
    Delete an organization
    """

    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.DELETE, f"/api/v2/organizations/{args.org_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        success_message="Organization deleted.",
        output_fmt=get_output_format(args),
    )

    if errors is None:
        env = args.env or Configuration.get_env()
        config_org_id = Configuration.get_organization_id(env)
        if args.org_id == config_org_id:
            Configuration.set_organization_id("", Configuration.get_env())
