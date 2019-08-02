# PYTHON_ARGCOMPLETE_OK
#
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

import sys

import colorama

from croud.clusters.commands import (
    clusters_delete,
    clusters_deploy,
    clusters_list,
    clusters_scale,
    clusters_upgrade,
)
from croud.config import Configuration, config_get, config_set
from croud.consumers.commands import (
    consumers_delete,
    consumers_deploy,
    consumers_edit,
    consumers_list,
)
from croud.login import login
from croud.logout import logout
from croud.me import me
from croud.monitoring.grafana.commands import set_grafana
from croud.organizations.commands import (
    organizations_create,
    organizations_delete,
    organizations_edit,
    organizations_list,
)
from croud.organizations.users.commands import (
    org_users_add,
    org_users_list,
    org_users_remove,
)
from croud.parser import Argument, create_parser
from croud.products.commands import products_list
from croud.projects.commands import project_create, project_delete, projects_list
from croud.projects.users.commands import (
    project_users_add,
    project_users_list,
    project_users_remove,
)
from croud.users.commands import users_list
from croud.users.roles.commands import roles_list

# fmt: off
command_tree = {
    "me": {
        "help": "Print information about the current logged in user.",
        "resolver": me,
    },
    "login": {"help": "Log in to CrateDB Cloud.", "resolver": login},
    "logout": {"help": "Log out of CrateDB Cloud.", "resolver": logout},
    "config": {
        "help": "Manage croud default configuration values.",
        "commands": {
            "get": {
                "help": "Get default configuration values.",
                "resolver": config_get,
                "noop_arg": {"choices": ["env", "region", "output-fmt"]},
                "omit_sudo": True,
            },
            "set": {
                "help": "Set default configuration values.",
                "resolver": config_set,
                "omit_sudo": True,
            },
        },
    },
    "consumers": {
        "help": "Manage consumers.",
        "commands": {
            "deploy": {
                "help": "Deploy a new consumer.",
                "extra_args": [
                    Argument(
                        "--product-name", type=str, required=True,
                        help="The product name to use.",
                    ),
                    Argument(
                        "--tier", type=str, required=True,
                        help="The product tier to use.",
                    ),
                    Argument(
                        "--consumer-name", type=str, required=True,
                        help="The consumer name to use.",
                    ),
                    Argument(
                        "--num-instances", type=int, default=1, required=False,
                        help="The number of instances to deploy.",
                    ),
                    Argument(
                        "--consumer-schema", type=str, required=True,
                        help=(
                            "The CrateDB database schema used by the Azure EventHub "
                            "consumer."
                        ),
                    ),
                    Argument(
                        "--consumer-table", type=str, required=True,
                        help=(
                            "The CrateDB database table used by the Azure EventHub "
                            "consumer."
                        ),
                    ),
                    Argument(
                        "-p", "--project-id", type=str, required=True,
                        help="The project ID to use.",
                    ),
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--eventhub-dsn", type=str, required=True,
                        help=(
                            "The connection string to the Azure EventHub from which to "
                            "consume."
                        ),
                    ),
                    Argument(
                        "--eventhub-consumer-group", type=str, required=True,
                        help=(
                            "The consumer group of the Azure EventHub from which to "
                            "consume."
                        ),
                    ),
                    Argument(
                        "--lease-storage-dsn", type=str, required=True,
                        help=(
                            "The connection string to an Azure storage account to use "
                            "as lease storage."
                        ),
                    ),
                    Argument(
                        "--lease-storage-container", type=str, required=True,
                        help=(
                            "The container name in the lease storage for the Azure "
                            "EventHub consumer to use."
                        ),
                    ),
                ],
                "resolver": consumers_deploy,
            },
            "list": {
                "help": "List all consumers the current user has access to.",
                "extra_args": [
                    Argument(
                        "-p", "--project-id", type=str, required=False,
                        help="The project ID to use.",
                    ),
                    Argument(
                        "--cluster-id", type=str, required=False,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--product-name", type=str, required=False,
                        help="The product name to use.",
                    ),
                ],
                "resolver": consumers_list,
            },
            "edit": {
                "help": "Edit the specified consumer set.",
                "extra_args": [
                    Argument(
                        "--consumer-id", type=str, required=True,
                        help="The consumer set ID to use.",
                    ),
                    Argument(
                        "--eventhub-dsn", type=str, required=False,
                        help=(
                            "The connection string to the Azure EventHub from which to "
                            "consume."
                        ),
                    ),
                    Argument(
                        "--eventhub-consumer-group", type=str, required=False,
                        help=(
                            "The consumer group of the Azure EventHub from which to "
                            "consume."
                        ),
                    ),
                    Argument(
                        "--lease-storage-dsn", type=str, required=False,
                        help=(
                            "The connection string to an Azure storage account to use "
                            "as lease storage."
                        ),
                    ),
                    Argument(
                        "--lease-storage-container", type=str, required=False,
                        help=(
                            "The container name in the lease storage for the Azure "
                            "EventHub consumer to use."
                        ),
                    ),
                    Argument(
                        "--consumer-schema", type=str, required=False,
                        help=(
                            "The CrateDB database schema used by the Azure EventHub "
                            "consumer."
                        ),
                    ),
                    Argument(
                        "--consumer-table", type=str, required=False,
                        help=(
                            "The CrateDB database table used by the Azure EventHub "
                            "consumer."
                        ),
                    ),
                    Argument(
                        "--cluster-id", type=str, required=False,
                        help="The CrateDB cluster ID to use.",
                    ),
                ],
                "resolver": consumers_edit,
            },
            "delete": {
                "help": "Delete the specified consumer set.",
                "extra_args": [
                    Argument(
                        "--consumer-id", type=str, required=True,
                        help="The consumer set ID to use.",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False)
                ],
                "resolver": consumers_delete,
            },
        },
    },
    "projects": {
        "help": "Manage projects.",
        "commands": {
            "create": {
                "help": "Create a project in the specified organization and region.",
                "extra_args": [
                    Argument(
                        "--name", type=str, required=True,
                        help="The project name to use.",
                    ),
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": project_create,
            },
            "delete": {
                "help": "Delete the specified project.",
                "extra_args": [
                    Argument(
                        "-p", "--project-id", type=str, required=True,
                        help="The project ID to use.",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False),
                ],
                "resolver": project_delete,
            },
            "list": {
                "help": (
                    "List all projects the current user has access to in "
                    "the specified region."
                ),
                "resolver": projects_list,
            },
            "users": {
                "help": "Manage users in projects.",
                "commands": {
                    "add": {
                        "help": "Add the selected user to a project.",
                        "extra_args": [
                            Argument(
                                "-p", "--project-id", type=str, required=True,
                                help="The project ID to use.",
                            ),
                            Argument(
                                "--user", type=str, required=True,
                                help="The user email address or ID to use.",
                            ),
                            Argument(
                                "--role", type=str, required=True,
                                help=(
                                    "The role FQN to use. Run `croud users roles list` "
                                    "for a list of available roles."
                                ),
                            ),
                        ],
                        "resolver": project_users_add,
                    },
                    "list": {
                        "help": "List all users within a project.",
                        "extra_args": [
                            Argument(
                                "-p", "--project-id", type=str, required=True,
                                help="The project ID to use.",
                            ),
                        ],
                        "resolver": project_users_list,
                    },
                    "remove": {
                        "help": "Remove the selected user from a project.",
                        "extra_args": [
                            Argument(
                                "-p", "--project-id", type=str, required=True,
                                help="The project ID to use.",
                            ),
                            Argument(
                                "--user", type=str, required=True,
                                help="The user email address or ID to use.",
                            ),
                        ],
                        "resolver": project_users_remove,
                    },
                },
            },
        },
    },
    "clusters": {
        "help": "Manage clusters.",
        "commands": {
            "list": {
                "help": "List all clusters the current user has access to.",
                "extra_args": [
                    Argument(
                        "-p", "--project-id", type=str, required=False,
                        help="The project ID to use.",
                    ),
                ],
                "resolver": clusters_list,
            },
            "deploy": {
                "help": "Deploy a new CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--product-name", type=str, required=True,
                        help="The product name to use.",
                    ),
                    Argument(
                        "--tier", type=str, required=True,
                        help="The product tier to use.",
                    ),
                    Argument(
                        "--unit", type=int, required=False,
                        help="The product scale unit to use.",
                    ),
                    Argument(
                        "-p", "--project-id", type=str, required=True,
                        help="The project ID to use.",
                    ),
                    Argument(
                        "--cluster-name", type=str, required=True,
                        help="The CrateDB cluster name to use.",
                    ),
                    Argument(
                        "--version", type=str, required=True,
                        help="The CrateDB version to use.",
                    ),
                    Argument(
                        "--username", type=str, required=True,
                        help="The CrateDB username to use.",
                    ),
                    Argument(
                        "--password", type=str, required=True,
                        help="The CrateDB password to use.",
                    ),
                    Argument(
                        "--channel", type=str, default="stable", required=False,
                        choices={"stable", "testing", "nightly"},
                        help="The channel of the CrateDB version (superusers only).",
                    ),
                ],
                "resolver": clusters_deploy,
            },
            "scale": {
                "help": "Scale an existing CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--unit", type=int, required=True,
                        help="The product scale unit to use.",
                    ),
                ],
                "resolver": clusters_scale,
            },
            "upgrade": {
                "help": "Upgrade an existing CrateDB cluster to a later version.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--version", type=str, required=True,
                        help="The CrateDB version to use.",
                    ),
                ],
                "resolver": clusters_upgrade
            },
            "delete": {
                "help": "Delete the specified cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False)
                ],
                "resolver": clusters_delete,
            },
        },
    },
    "products": {
        "help": "Manage Products.",
        "commands": {
            "list": {
                "help": "List all available products in the current region.",
                "extra_args": [
                    Argument(
                        "--kind", type=str, required=False, help="The product kind."
                    ),
                ],
                "resolver": products_list,
            },
        },
    },
    "organizations": {
        "help": "Manage organizations.",
        "commands": {
            "create": {
                "help": "Create a new organization.",
                "extra_args": [
                    Argument(
                        "--name", type=str, required=True,
                        help="The organization name to use.",
                    ),
                    Argument(
                        "--plan-type", type=int, required=False,
                        choices=[1, 2, 3, 4, 5, 6],
                        help="The support plan to use for the organization. Argument "
                             "is for superusers only.",
                    ),
                ],
                "resolver": organizations_create,
            },
            "list": {
                "help": "List all organizations the current user has access to.",
                "resolver": organizations_list,
            },
            "edit": {
                "help": "Edit the specified organization.",
                "extra_args": [
                    Argument(
                        "--name", type=str, required=False,
                        help="The new organization name to use.",
                    ),
                    Argument(
                        "--plan-type", type=int, required=False,
                        choices=[1, 2, 3, 4, 5, 6],
                        help="The new support plan to use for the organization.",
                    ),
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": organizations_edit,
            },
            "delete": {
                "help": "Delete the specified organization.",
                "extra_args": [
                    Argument("-y", "--yes", action="store_true", default=False),
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": organizations_delete,
            },
            "users": {
                "help": "Manage users in an organization.",
                "commands": {
                    "add": {
                        "help": "Add the selected user to an organization.",
                        "extra_args": [
                            Argument(
                                "--user", type=str, required=True,
                                help="The user email address or ID to use.",
                            ),
                            Argument(
                                "--role", type=str, required=True,
                                help=(
                                    "The role FQN to use. Run `croud users roles list` "
                                    "for a list of available roles."
                                ),
                            ),
                            Argument(
                                "--org-id", type=str, required=False,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": org_users_add,
                    },
                    "list": {
                        "help": "List all users within an organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=False,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": org_users_list,
                    },
                    "remove": {
                        "help": "Remove the selected user from an organization.",
                        "extra_args": [
                            Argument(
                                "--user", type=str, required=True,
                                help="The user email address or ID to use.",
                            ),
                            Argument(
                                "--org-id", type=str, required=False,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": org_users_remove,
                    },
                },
            },
        },
    },
    "users": {
        "help": "Manage users.",
        "commands": {
            "list": {
                "help": "List all users.",
                "extra_args": [
                    Argument(
                        "--no-roles", action="store_true",
                        help="List users without roles.",
                    ),
                    Argument(
                        "--no-org", action="store_true",
                        help="Only show users that are not part of any organization.",
                    )
                ],
                "resolver": users_list,
            },
            "roles": {
                "help": "Manage user roles.",
                "commands": {
                    "list": {
                        "help": "List all available roles.",
                        "resolver": roles_list,
                    },
                },
            },
        },
    },
    "monitoring": {
        "help": "Manage monitoring tools.",
        "commands": {
            "grafana": {
                "help": "Manage access to Grafana dashboards for projects.",
                "commands": {
                    "enable": {
                        "help": "Enable Grafana dashboards to visualize metrics for a "
                        "project.",
                        "extra_args": [
                            Argument(
                                "-p", "--project-id", type=str, required=True,
                                help="The project ID to use.",
                            ),
                        ],
                        "resolver": lambda args: set_grafana(True, args),
                    },
                    "disable": {
                        "help": "Disable Grafana dashboards for a project.",
                        "extra_args": [
                            Argument(
                                "-p", "--project-id", type=str, required=True,
                                help="The project ID to use.",
                            ),
                        ],
                        "resolver": lambda args: set_grafana(False, args),
                    },
                },
            },
        }
    }
}
# fmt: on


def get_parser():
    tree = {
        "help": "A command line interface for CrateDB Cloud.",
        "commands": command_tree,
    }
    return create_parser(tree)


def main():
    Configuration.create()
    colorama.init()

    parser = get_parser()
    params = parser.parse_args(sys.argv[1:])
    if "resolver" in params:
        fn = params.resolver
        del params.resolver
        fn(params)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
