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


def api_keys_list(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get("/api/v2/users/me/api-keys/")

    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
        keys=["user_id", "key", "active", "last_used"],
    )


def api_keys_create(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.post("/api/v2/users/me/api-keys/")

    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
        keys=["user_id", "key", "active", "secret"],
    )


def api_keys_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(f"/api/v2/users/me/api-keys/{args.api_key}/")

    print_response(
        data=data,
        errors=errors,
        success_message="API key deleted.",
        output_fmt=get_output_format(args),
    )


def api_keys_edit(args: Namespace) -> None:
    body = {"active": args.active == "true"}
    client = Client.from_args(args)
    data, errors = client.patch(f"/api/v2/users/me/api-keys/{args.api_key}/", body=body)

    print_response(
        data=data,
        errors=errors,
        success_message="API key edited.",
        output_fmt=get_output_format(args),
        keys=["key", "active"],
    )
