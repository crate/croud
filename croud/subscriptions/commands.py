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


def subscriptions_create(args: Namespace) -> None:
    body = {"type": args.type, "organization_id": args.org_id}
    client = Client.from_args(args)
    data, errors = client.post("/api/v2/subscriptions/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "state", "provider"],
        success_message="Subscription created.",
        output_fmt=get_output_format(args),
    )


def subscriptions_get(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/subscriptions/{args.id}/")
    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
    )


def subscriptions_list(args: Namespace) -> None:
    client = Client.from_args(args)
    if args.org_id:
        url = f"/api/v2/organizations/{args.org_id}/subscriptions/"
    else:
        url = "/api/v2/subscriptions/"
    data, errors = client.get(url)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "organization_id", "state", "provider"],
        output_fmt=get_output_format(args),
    )


@require_confirmation(
    "Are you sure you want to cancel this subscription? "
    "This will delete any clusters running in this subscription.",
    cancel_msg="Deletion cancelled.",
)
def subscription_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(f"/api/v2/subscriptions/{args.subscription_id}/")
    print_response(
        data=data,
        errors=errors,
        success_message="Subscription cancelled.",
        keys=["id", "name", "organization_id", "state", "provider"],
        output_fmt=get_output_format(args),
    )
