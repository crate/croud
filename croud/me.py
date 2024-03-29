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


def me(args: Namespace) -> None:
    """
    Prints the current logged in user
    """

    client = Client.from_args(args)
    data, errors = client.get("/api/v2/users/me/")
    print_response(
        data=data,
        errors=errors,
        keys=["email", "username", "idp"],
        output_fmt=get_output_format(args),
    )


def me_edit(args: Namespace) -> None:
    """
    Lets the user edit their data
    """

    body = {}
    if args.email:
        body["email"] = args.email

    client = Client.from_args(args)
    data, errors = client.patch("/api/v2/users/me/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["success", "status", "message"],
        output_fmt=get_output_format(args),
    )
