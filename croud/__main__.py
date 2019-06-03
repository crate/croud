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
from croud.cmd import (
    cluster_id_arg,
    cluster_name_arg,
    consumer_id_arg,
    consumer_name_arg,
    consumer_schema_arg,
    consumer_table_arg,
    crate_password_arg,
    crate_username_arg,
    crate_version_arg,
    eventhub_consumer_group_arg,
    eventhub_dsn_arg,
    kind_arg,
    lease_storage_container_arg,
    lease_storage_dsn_arg,
    num_instances_arg,
    org_id_arg,
    org_id_no_org_arg_mutual_exclusive,
    org_name_arg,
    org_plan_type_arg,
    product_name_arg,
    product_tier_arg,
    product_unit_arg,
    project_id_arg,
    project_name_arg,
    resource_id_arg,
    role_fqn_arg,
    user_id_arg,
    user_id_or_email_arg,
    yes_arg,
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
from croud.organizations.commands import organizations_create, organizations_list
from croud.organizations.users.commands import org_users_add, org_users_remove
from croud.parser import create_parser
from croud.products.commands import products_list
from croud.projects.commands import project_create, projects_list
from croud.projects.users.commands import project_user_add, project_user_remove
from croud.users.commands import users_list
from croud.users.roles.commands import roles_add, roles_list, roles_remove

# fmt: off
command_tree = {
    "me": {
        "help": "Print information about the current logged in user.",
        "extra_args": [],
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
            },
            "set": {
                "help": "Set default configuration values.",
                "extra_args": [],
                "resolver": config_set,
            },
        },
    },
    "consumers": {
        "help": "Manage consumers.",
        "commands": {
            "deploy": {
                "help": "Deploy a new consumer.",
                "extra_args": [
                    lambda req_opt_group, opt_opt_group: product_name_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    product_tier_arg,
                    consumer_name_arg,
                    num_instances_arg,
                    lambda req_opt_group, opt_opt_group: consumer_schema_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: consumer_table_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: project_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: cluster_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: eventhub_dsn_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: eventhub_consumer_group_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: lease_storage_dsn_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: lease_storage_container_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                ],
                "resolver": consumers_deploy,
            },
            "list": {
                "help": "List all consumers the current user has access to.",
                "extra_args": [
                    lambda req_opt_group, opt_opt_group: project_id_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group: cluster_id_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group: product_name_arg(
                        req_opt_group, opt_opt_group, False
                    )
                ],
                "resolver": consumers_list,
            },
            "edit": {
                "help": "Edit the specified consumer set.",
                "extra_args": [
                    consumer_id_arg,
                    lambda req_opt_group, opt_opt_group:
                    eventhub_dsn_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group:
                    eventhub_consumer_group_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group:
                    lease_storage_dsn_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group:
                    lease_storage_container_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group:
                    consumer_schema_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group:
                    consumer_table_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group:
                    cluster_id_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                ],
                "resolver": consumers_edit,
            },
            "delete": {
                "help": "Delete the specified consumer set.",
                "extra_args": [
                    consumer_id_arg,
                    yes_arg
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
                    project_name_arg,
                    lambda req_opt_group, opt_opt_group: org_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                ],
                "resolver": project_create,
            },
            "list": {
                "help": (
                    "List all projects the current user has access to in "
                    "the specified region."
                ),
                "extra_args": [],
                "resolver": projects_list,
            },
            "users": {
                "help": "Manage users in projects.",
                "commands": {
                    "add": {
                        "help": "Add the selected user to a project.",
                        "extra_args": [
                            lambda req_opt_group, opt_opt_group: project_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                            user_id_or_email_arg,
                        ],
                        "resolver": project_user_add,
                    },
                    "remove": {
                        "help": "Remove the selected user from a project.",
                        "extra_args": [
                            lambda req_opt_group, opt_opt_group: project_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                            user_id_or_email_arg,
                        ],
                        "resolver": project_user_remove,
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
                    lambda req_opt_group, opt_opt_group: project_id_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                ],
                "resolver": clusters_list,
            },
            "deploy": {
                "help": "Deploy a new CrateDB cluster.",
                "extra_args": [
                    lambda req_opt_group, opt_opt_group: product_name_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    product_tier_arg,
                    lambda req_opt_group, opt_opt_group: product_unit_arg(
                        req_opt_group, opt_opt_group, False
                    ),
                    lambda req_opt_group, opt_opt_group: project_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: cluster_name_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    crate_version_arg,
                    crate_username_arg,
                    crate_password_arg,
                ],
                "resolver": clusters_deploy,
            },
            "scale": {
                "help": "Scale an existing CrateDB cluster.",
                "extra_args": [
                    lambda req_opt_group, opt_opt_group: cluster_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    lambda req_opt_group, opt_opt_group: product_unit_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                ],
                "resolver": clusters_scale,
            },
            "upgrade": {
                "help": "Upgrade an existing CrateDB cluster to a later version.",
                "extra_args": [
                    lambda req_opt_group, opt_opt_group: cluster_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    crate_version_arg,
                ],
                "resolver": clusters_upgrade
            },
            "delete": {
                "help": "Delete the specified cluster.",
                "extra_args": [
                    lambda req_opt_group, opt_opt_group: cluster_id_arg(
                        req_opt_group, opt_opt_group, True
                    ),
                    yes_arg
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
                "extra_args": [kind_arg],
                "resolver": products_list,
            },
        },
    },
    "organizations": {
        "help": "Manage organizations.",
        "commands": {
            "create": {
                "help": "Create a new organization.",
                "extra_args": [org_name_arg, org_plan_type_arg],
                "resolver": organizations_create,
            },
            "list": {
                "help": "List all organizations the current user has access to.",
                "extra_args": [],
                "resolver": organizations_list,
            },
            "users": {
                "help": "Manage users in an organization.",
                "commands": {
                    "add": {
                        "help": "Add the selected user to an organization.",
                        "extra_args": [
                            user_id_or_email_arg,
                            lambda req_opt_group, opt_opt_group: role_fqn_arg(
                                req_opt_group, opt_opt_group, False
                            ),
                            lambda req_opt_group, opt_opt_group: org_id_arg(
                                req_opt_group, opt_opt_group, False
                            ),
                        ],
                        "resolver": org_users_add,
                    },
                    "remove": {
                        "help": "Remove the selected user from an organization.",
                        "extra_args": [
                            user_id_or_email_arg,
                            lambda req_opt_group, opt_opt_group: org_id_arg(
                                req_opt_group, opt_opt_group, False
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
                "help": "List all users within the specified organization.",
                "extra_args": [
                    org_id_no_org_arg_mutual_exclusive,
                ],
                "resolver": users_list,
            },
            "roles": {
                "help": "Manage user roles.",
                "commands": {
                    "add": {
                        "help": "Assign a role to the selected user.",
                        "extra_args": [
                            lambda req_opt_group, opt_opt_group: resource_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                            lambda req_opt_group, opt_opt_group: user_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                            lambda req_opt_group, opt_opt_group: role_fqn_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                        ],
                        "resolver": roles_add,
                    },
                    "remove": {
                        "help": "Unassign a role from the selected user.",
                        "extra_args": [
                            lambda req_opt_group, opt_opt_group: resource_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                            lambda req_opt_group, opt_opt_group: user_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                            lambda req_opt_group, opt_opt_group: role_fqn_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                        ],
                        "resolver": roles_remove,
                    },
                    "list": {
                        "help": "List all available roles.",
                        "extra_args": [],
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
                            lambda req_opt_group, opt_opt_group: project_id_arg(
                                req_opt_group, opt_opt_group, True
                            ),
                        ],
                        "resolver": lambda args: set_grafana(True, args),
                    },
                    "disable": {
                        "help": "Disable Grafana dashboards for a project.",
                        "extra_args": [
                            lambda req_opt_group, opt_opt_group: project_id_arg(
                                req_opt_group, opt_opt_group, True
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
