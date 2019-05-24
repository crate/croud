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

from argparse import _ArgumentGroup


def yes_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument("-y", "--yes", action="store_true", default=False)


def project_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "-p", "--project-id", type=str, help="The project ID to use.", required=required
    )


def project_name_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--name", type=str, help="The project name to use.", required=True
    )


def org_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--org-id", type=str, help="The organization ID to use.", required=required
    )


def no_org_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument(
        "--no-org",
        nargs="?",
        default=False,
        const=True,
        type=bool,
        help="Only show users that are not part of any organization.",
    )


def org_id_no_org_arg_mutual_exclusive(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup
) -> None:
    exclusive = opt_args.add_mutually_exclusive_group()
    org_id_arg(req_args, exclusive, False)
    no_org_arg(req_args, exclusive)


def org_name_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--name", type=str, help="The organization name to use.", required=True
    )


def org_plan_type_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--plan-type",
        choices=[1, 2, 3, 4, 5, 6],
        type=int,
        help="The support plan to use for the organization.",
        required=True,
    )


def resource_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--resource", type=str, help="The resource ID to use.", required=required
    )


def role_fqn_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--role",
        type=str,
        help=(
            "The role FQN to use. Run `croud users roles list` "
            "for a list of available roles."
        ),
        required=required,
    )


def user_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--user", type=str, help="The user ID to use.", required=required
    )


def user_id_or_email_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--user", type=str, help="The user email address or ID to use.", required=True
    )


def cluster_id_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--cluster-id",
        type=str,
        help="The CrateDB cluster ID to use.",
        required=required,
    )


def cluster_name_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--cluster-name",
        type=str,
        help="The CrateDB cluster name to use.",
        required=required,
    )


def product_tier_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--tier", type=str, help="The product tier to use.", required=True
    )


def product_unit_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--unit", type=int, help="The product scale unit to use.", required=required
    )


def product_name_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--product-name", type=str, help="The product name to use.", required=required
    )


def crate_version_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--version", type=str, help="The CrateDB version to use.", required=True
    )


def crate_username_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--username", type=str, help="The CrateDB username to use.", required=True
    )


def crate_password_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--password", type=str, help="The CrateDB password to use.", required=True
    )


def consumer_id_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--consumer-id", type=str, help="The consumer set ID to use.", required=True
    )


def consumer_name_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    req_args.add_argument(
        "--consumer-name", type=str, help="The consumer name to use.", required=True
    )


def consumer_schema_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool = True
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-schema",
        type=str,
        help="The CrateDB database schema used by the Azure EventHub consumer.",
        required=required,
    )


def consumer_table_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool = True
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--consumer-table",
        type=str,
        help="The CrateDB database table used by the Azure EventHub consumer.",
        required=required,
    )


def eventhub_dsn_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool = True
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--eventhub-dsn",
        type=str,
        help="The connection string to the Azure EventHub from which to consume.",
        required=required,
    )


def eventhub_consumer_group_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool = True
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--eventhub-consumer-group",
        type=str,
        help="The consumer group of the Azure EventHub from which to consume.",
        required=required,
    )


def lease_storage_dsn_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool = True
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--lease-storage-dsn",
        type=str,
        help=(
            "The connection string to an Azure storage account to use as lease storage."
        ),
        required=required,
    )


def lease_storage_container_arg(
    req_args: _ArgumentGroup, opt_args: _ArgumentGroup, required: bool = True
) -> None:
    group = req_args if required else opt_args
    group.add_argument(
        "--lease-storage-container",
        type=str,
        help=(
            "The container name in the lease storage for the Azure EventHub "
            "consumer to use."
        ),
        required=required,
    )


def num_instances_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument(
        "--num-instances",
        type=int,
        help="The number of instances to deploy.",
        default=1,
        required=False,
    )


def kind_arg(req_args: _ArgumentGroup, opt_args: _ArgumentGroup) -> None:
    opt_args.add_argument("--kind", type=str, help="The product kind.", required=False)
