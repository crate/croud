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


def organizations_create(args: Namespace) -> None:
    """
    Creates an organization
    """

    client = Client.from_args(args)
    client.send(
        RequestMethod.POST,
        "/api/v2/organizations/",
        body={"name": args.name, "plan_type": args.plan_type},
    )
    client.print(keys=["id", "name", "plan_type"])


def organizations_list(args: Namespace) -> None:
    """
    Lists organizations
    """

    client = Client.from_args(args)
    client.send(RequestMethod.GET, "/api/v2/organizations/")
    client.print(keys=["id", "name", "plan_type"])


@require_confirmation(
    "Are you sure you want to delete the organization?",
    cancel_msg="Organization deletion cancelled.",
)
def organizations_delete(args: Namespace) -> None:
    """
    Delete an organization
    """

    client = Client.from_args(args)
    client.send(RequestMethod.DELETE, f"/api/v2/organizations/{args.org_id}/")
    client.print("Organization deleted.")
