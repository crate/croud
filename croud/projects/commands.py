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

from croud.rest import Client
from croud.session import RequestMethod
from croud.util import require_confirmation


def project_create(args: Namespace) -> None:
    """
    Creates a project in the organization the user belongs to.
    """

    client = Client.from_args(args)
    client.send(
        RequestMethod.POST,
        "/api/v2/projects/",
        body={"name": args.name, "organization_id": args.org_id},
    )
    client.print(keys=["id"])


@require_confirmation(
    "Are you sure you want to delete the project?",
    cancel_msg="Project deletion cancelled.",
)
def project_delete(args: Namespace) -> None:
    """
    Deletes a project in the organization the user belongs to.
    """
    client = Client.from_args(args)
    client.send(RequestMethod.DELETE, f"/api/v2/projects/{args.project_id}/")
    client.print("Project deleted.")


def projects_list(args: Namespace) -> None:
    """
    Lists all projects for the current user in the specified region
    """

    client = Client.from_args(args)
    client.send(RequestMethod.GET, "/api/v2/projects/")
    client.print(keys=["id", "name", "region", "organization_id"])
