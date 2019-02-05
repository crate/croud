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

from croud.gql import Query, print_query


def product_deploy(args: Namespace) -> None:
    """
    Deploy a new CrateDB Cloud for Azure IoT product.
    """

    _query = f"""
mutation {{
    createProduct(
        tier: "{args.tier}",
        unit: {args.unit},
        projectId: "{args.project_id}",
        name: "{args.product_name}",
        cluster: {{
            version: "{args.version}",
            username: "{args.username}",
            password: "{args.password}"
        }},
        consumer: {{
            eventhub: {{
                connectionString: "{args.consumer_eventhub_connection_string}",
                consumerGroup: "{args.consumer_eventhub_consumer_group}",
                leaseStorage: {{
                    connectionString: "{args.consumer_eventhub_lease_storage_connection_string}",
                    container: "{args.consumer_eventhub_lease_storage_container}"
                }}
            }},
            schema: "{args.consumer_schema}",
            table: "{args.consumer_table}"
        }}
    ) {{
        id,
        url
    }}
}}
    """  # noqa

    query = Query(_query, args, endpoint="/product/graphql")
    query.execute()
    print_query(query, "createProduct")
