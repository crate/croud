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

import bitmath

from croud.api import Client
from croud.config import get_output_format
from croud.printer import print_response


def products_list(args: Namespace) -> None:
    client = Client.from_args(args)
    url = "/api/v2/products/"
    data, errors = client.get(url, params={"kind": args.kind} if args.kind else None)
    filtered = {}
    for product in data:  # type: ignore
        # Ignore deprecated products and products that have no price associated.
        if product.get("deprecated", False):
            continue
        if not product.get("price_per_dtu_minute"):
            continue
        # group by kind/name/tier tuples to remove duplicates for providers and regions
        key = f"{product['kind']}{product['name']}{product['tier']}"
        product["vcpu_cores"] = product.get("specs", {}).get("cpu_cores")
        product["ram"] = product.get("specs", {}).get("ram_bytes", 0)
        product["min_storage"] = product.get("specs", {}).get("storage_minimum_bytes")
        product["max_storage"] = product.get("specs", {}).get("storage_maximum_bytes")
        filtered[key] = product
    print_response(
        data=list(filtered.values()),
        errors=errors,
        keys=[
            "kind",
            "name",
            "tier",
            "description",
            "scale_summary",
            "vcpu_cores",
            "ram",
            "min_storage",
            "max_storage",
        ],
        output_fmt=get_output_format(args),
        transforms={
            "ram": bytes_to_gib,
            "min_storage": bytes_to_gib,
            "max_storage": bytes_to_gib,
        },
    )


def bytes_to_gib(size_bytes):
    if not size_bytes:
        return None
    return str(bitmath.Byte(size_bytes).to_GiB())
