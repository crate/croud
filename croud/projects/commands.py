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
from croud.util import org_id_config_fallback, require_confirmation


@org_id_config_fallback
def project_create(args: Namespace) -> None:
    """
    Creates a project in the organization the user belongs to.
    """

    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.POST,
        "/api/v2/projects/",
        body={"name": args.name, "organization_id": args.org_id},
    )
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
    """
    Deletes a project in the organization the user belongs to.
    """
    client = Client.from_args(args)
    data, errors = client.send(
        RequestMethod.DELETE, f"/api/v2/projects/{args.project_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        success_message="Project deleted.",
        output_fmt=get_output_format(args),
    )


def projects_list(args: Namespace) -> None:
    """
    Lists all projects for the current user in the specified region
    """

    client = Client.from_args(args)
    data, errors = client.send(RequestMethod.GET, "/api/v2/projects/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "region", "organization_id"],
        output_fmt=get_output_format(args),
    )
