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
import shtab

from croud.apikeys.commands import (
    api_keys_create,
    api_keys_delete,
    api_keys_edit,
    api_keys_list,
)
from croud.cloud_configurations.commands import (
    cloud_configurations_get,
    cloud_configurations_list,
    cloud_configurations_set,
)
from croud.clusters.commands import (
    clusters_delete,
    clusters_deploy,
    clusters_expand_storage,
    clusters_get,
    clusters_list,
    clusters_restart_node,
    clusters_scale,
    clusters_set_backup_schedule,
    clusters_set_deletion_protection,
    clusters_set_ip_whitelist,
    clusters_set_product,
    clusters_set_suspended,
    clusters_snapshots_list,
    clusters_snapshots_restore,
    clusters_subscription_update,
    clusters_upgrade,
    create_scheduled_job,
    delete_scheduled_job,
    edit_scheduled_job,
    export_jobs_create,
    export_jobs_delete,
    export_jobs_list,
    get_scheduled_job_log,
    get_scheduled_jobs,
    import_jobs_create_from_azure_blob_storage,
    import_jobs_create_from_dynamodb,
    import_jobs_create_from_file,
    import_jobs_create_from_s3,
    import_jobs_create_from_url,
    import_jobs_delete,
    import_jobs_list,
)
from croud.config import CONFIG
from croud.config.commands import (
    config_add_profile,
    config_current_profile,
    config_remove_profile,
    config_set_profile,
    config_show,
)
from croud.login import login
from croud.logout import logout
from croud.me import me, me_edit
from croud.organizations.auditlogs.commands import auditlogs_list
from croud.organizations.commands import (
    org_credits_create,
    org_credits_edit,
    org_credits_expire,
    org_credits_list,
    org_customer_edit,
    org_customer_get,
    org_files_create,
    org_files_delete,
    org_files_get,
    org_files_list,
    org_secrets_create,
    org_secrets_delete,
    org_secrets_list,
    organizations_create,
    organizations_delete,
    organizations_edit,
    organizations_get,
    organizations_list,
)
from croud.organizations.users.commands import (
    org_users_add,
    org_users_list,
    org_users_remove,
)
from croud.parser import Argument, create_parser
from croud.printer import print_error, print_info
from croud.products.commands import products_list
from croud.projects.commands import (
    project_create,
    project_delete,
    project_edit,
    projects_get,
    projects_list,
)
from croud.projects.users.commands import (
    project_users_add,
    project_users_list,
    project_users_remove,
)
from croud.regions.commands import regions_create, regions_delete, regions_list
from croud.subscriptions.commands import (
    subscription_delete,
    subscriptions_create,
    subscriptions_get,
    subscriptions_list,
)
from croud.tools.spinner import HALO
from croud.users.commands import users_delete, users_list
from croud.users.roles.commands import roles_list
from croud.util import asbool

# Arguments common to all import-job create commands
import_job_create_common_args = [
    Argument(
        "--cluster-id",
        type=str,
        required=True,
        help="The cluster the data will be imported into.",
    ),
    Argument(
        "--table",
        type=str,
        required=True,
        help="The table the data will be imported into.",
    ),
    Argument(
        "--create-table",
        type=lambda x: asbool(x),
        required=False,
        choices=[True, False],
        help="Whether the table should be created automatically"
        " if it does not exist. If true new columns will also be added when the data"
        " requires them.",
    ),
]

import_job_create_common_file_args = [
    Argument(
        "--file-format",
        type=str,
        required=True,
        choices=["csv", "json", "parquet"],
        help="The format of the structured data in the file.",
    ),
    Argument(
        "--compression",
        type=str,
        required=False,
        choices=["gzip", "none"],
        help="The compression method the file uses.",
    ),
    Argument(
        "--transformations",
        type=str,
        required=False,
        help="The transformations to apply when fetching data. This is the SELECT "
        "statement from an SQL query that is executed on the loaded data before "
        "inserting into CrateDB. "
        "This can be used to apply arbitrary SQL functions on your data before "
        "inserting into CrateDB, i.e. `UNNEST()`, `SUM()` and similar.",
    ),
]

# fmt: off
command_tree = {
    "me": {
        "help": "Print information about the current logged in user.",
        "resolver": me,
        "commands": {
            "edit": {
                "help": "Edit your own email address.",
                "extra_args": [
                    Argument(
                        "--email", type=str, required=True,
                        help="The new email address to use."
                    ),
                ],
                "resolver": me_edit,
            },
        }
    },
    "login": {
        "help": "Log in to your CrateDB Cloud account.",
        "resolver": login,
        "extra_args": [
            Argument(
                "--idp", type=str, required=True,
                choices=["cognito", "azuread", "github", "google"],
                help="The identity provider (IdP) for the login."
            ),
        ],
    },
    "logout": {"help": "Log out of your CrateDB Cloud account.", "resolver": logout},
    "config": {
        "help": "Manage croud configuration.",
        "commands": {
            "show": {
                "help": "Show the full configuration.",
                "resolver": config_show,
                "omit": {"sudo", "region", "format"},
            },
            "profiles": {
                "help": "Manage configuration profiles.",
                "commands": {
                    "current": {
                        "help": "Print the current profile.",
                        "resolver": config_current_profile,
                        "omit": {"sudo", "region"},
                    },
                    "use": {
                        "help": "Switch to a different profile.",
                        "resolver": config_set_profile,
                        "omit": {"sudo", "region"},
                        "extra_args": [
                            Argument(
                                "profile", type=str,
                                help="The name of the profile that should be used."
                            ),
                        ],
                    },
                    "add": {
                        "help": "Add a new profile to your configuration.",
                        "resolver": config_add_profile,
                        "omit": {"sudo", "region", "format"},
                        "extra_args": [
                            Argument(
                                "profile", type=str,
                                help="The name of the profile that should be added."
                            ),
                            Argument(
                                "--endpoint", type=str, required=True,
                                help="The API endpoint for the profile."
                            ),
                            Argument(
                                "--format", type=str, required=False,
                                help="The output format for the profile."
                            ),
                            Argument(
                                "--region", type=str, required=False,
                                help="The region for the profile."
                            ),
                        ],
                    },
                    "remove": {
                        "help": "Remove a profile from your configuration.",
                        "resolver": config_remove_profile,
                        "omit": {"sudo", "region", "format"},
                        "extra_args": [
                            Argument(
                                "profile", type=str,
                                help="The name of the profile that should be removed."
                            ),
                        ],
                    },
                },
            },
        },
    },
    "projects": {
        "help": "Manage projects. It's an internal resource that contains clusters.",
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
                    Argument(
                        "--backup-location-type",
                        choices=["s3"],
                        type=str,
                        required=False,
                        help="CrateDB Edge regions only. "
                             "The type of the custom backup location to use. "
                             "Only 's3' currently supported. "
                    ),
                    Argument(
                        "--backup-location", type=str, required=False,
                        help="CrateDB Edge regions only. "
                             "The location of where backups are to be stored, "
                             "i.e. name of s3 bucket for s3 locations. "
                    ),
                    Argument(
                        "--backup-location-access-key-id", type=str, required=False,
                        help="CrateDB Edge regions only. "
                             "The AWS access key id for the given s3 bucket. "
                    ),
                    Argument(
                        "--backup-location-endpoint-url", type=str, required=False,
                        help="CrateDB Edge regions only. "
                             "The URL to a S3 compatible endpoint. "
                    ),
                    Argument(
                        "--backup-location-secret-access-key", type=str, required=False,
                        help="CrateDB Edge regions only. "
                             "The AWS secret access key for the given s3 bucket. "
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
            "edit": {
                "help": "Rename the specified project.",
                "extra_args": [
                    Argument(
                        "-p", "--project-id", type=str, required=True,
                        help="The project ID to use.",
                    ),
                    Argument(
                        "--name", type=str, required=False,
                        help="The new project name to use.",
                    ),
                ],
                "resolver": project_edit,
            },
            "get": {
                "help": (
                    "Get a project by its ID."
                ),
                "extra_args": [
                    Argument(
                        "id", type=str,
                        help="The ID of the project.",
                    ),
                ],
                "resolver": projects_get,
            },
            "list": {
                "help": (
                    "List all projects the current user has access to in "
                    "the specified organization."
                ),
                "extra_args": [
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": projects_list,
            },
            "users": {
                "help": "Manage users in projects.",
                "commands": {
                    "add": {
                        "help": "Add a user to a project. It allows the user to access "
                                "the project and its clusters with the specified role.",
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
                                    "The role FQN to use. Run ``croud users roles "
                                    "list`` for a list of available roles."
                                ),
                            ),
                        ],
                        "resolver": project_users_add,
                    },
                    "list": {
                        "help": "List the users who have access to a project.",
                        "extra_args": [
                            Argument(
                                "-p", "--project-id", type=str, required=True,
                                help="The project ID to use.",
                            ),
                        ],
                        "resolver": project_users_list,
                    },
                    "remove": {
                        "help": "Remove a user from a project.",
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
        "help": "Manage CrateDB clusters.",
        "commands": {
            "get": {
                "help": (
                    "Get a cluster by its ID."
                ),
                "extra_args": [
                    Argument(
                        "id", type=str,
                        help="The ID of the cluster.",
                    ),
                ],
                "resolver": clusters_get,
            },
            "list": {
                "help": "List all clusters the current user has access to.",
                "extra_args": [
                    Argument(
                        "-p", "--project-id", type=str, required=False,
                        help="The project ID to use. We recommend using the org-id "
                             "instead",
                    ),
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": clusters_list,
            },
            "deploy": {
                "help": "Deploy a new CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--product-name", type=str, required=True,
                        help="The product name to use. "
                             "Run ``croud products list --kind cluster`` to get "
                             "the list of available products.",
                    ),
                    Argument(
                        "--tier", type=str, required=True,
                        help="The product tier to use. "
                             "Run ``croud products list --kind cluster`` to get "
                             "the products tier.",
                    ),
                    Argument(
                        "--unit", type=int, required=False,
                        help="The product scale unit to use (0 means 1 node, "
                             "1 means 2 nodes, etc). "
                             "Run ``croud products list --kind cluster`` to get the "
                             "products available scale units.",
                    ),
                    Argument(
                        "--master-product-name", type=str, required=False,
                        help="Optional dedicated master-node product (e.g. "
                             "'master_cr2'). Only valid for products that offer "
                             "dedicated masters (CR3/CR4/CR5). Omit for a cluster "
                             "without dedicated master nodes.",
                    ),
                    Argument(
                        "-p", "--project-id", type=str,
                        required=False,
                        help="The project ID to use. We recommend using the org-id "
                             "instead",
                    ),
                    Argument(
                        "--org-id", type=str,
                        required=False,
                        help="The organization ID to use. "
                             "Defaults to the global configuration value.",
                    ),
                    Argument(
                        "--cluster-name", type=str, required=True,
                        help="The CrateDB cluster name to use. It must be a URL-safe "
                             "string.",
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
                        help="The CrateDB password to use. Minimum 24 characters.",
                    ),
                    Argument(
                        "--subscription-id", type=str, required=True,
                        help="The subscription to use for billing of this cluster. Use "
                             "``free_tier`` to deploy a free cluster. "
                             "Run ``croud subscriptions list`` to get the "
                             "available subscriptions.",
                    ),
                    Argument(
                        "--channel", type=str, default="stable", required=False,
                        choices=["stable", "testing", "nightly"],
                        help="The channel of the CrateDB version.",
                    ),
                    Argument(
                        "--cpus", type=float, required=False,
                        help="CrateDB Edge regions only. "
                             "Number of CPU cores to allocate. Can be fractional.",
                    ),
                    Argument(
                        "--disks", type=int, required=False,
                        help="CrateDB Edge regions only. Number of disks to attach.",
                    ),
                    Argument(
                        "--disk-size-gb", type=int, required=False,
                        help="Size of disks to attach (in GiB).",
                    ),
                    Argument(
                        "--disk-type", type=str, required=False,
                        choices=["standard", "premium"],
                        help="CrateDB Edge regions only. Type of disks to use.",
                    ),
                    Argument(
                        "--memory-size-mb", type=int, required=False,
                        help="CrateDB Edge regions only. "
                             "Amount of memory to allocate (in MiB).",
                    ),
                ],
                "resolver": clusters_deploy,
            },
            "scale": {
                "help": "Scale an existing cluster up or down by changing the "
                        "number of nodes.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--unit", type=int, required=True,
                        help="The product scale unit to use (0 means 1 node, "
                             "1 means 2 nodes, etc). "
                             "Run ``croud products list --kind cluster`` to get the "
                             "products available scale units.",
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
            "restart-node": {
                "help": "Restart a node in a CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--ordinal", type=int, required=True,
                        help="The ordinal index of the node to restart.",
                    ),
                ],
                "resolver": clusters_restart_node,
            },
            "set-deletion-protection": {
                "help": "Change the deletion protection status of a cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--value", type=lambda x: asbool(x),
                        required=True, help="The deletion protection status",
                        choices=[True, False],
                    ),
                ],
                "resolver": clusters_set_deletion_protection,
            },
            "set-ip-whitelist": {
                "help": "Set IP Network Whitelist in CIDR format (comma-separated).",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--net", type=str,
                        required=True,
                        help="IP Network list in CIDR format (comma-separated).",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False)
                ],
                "resolver": clusters_set_ip_whitelist,
            },
            "expand-storage": {
                "help": "Expand storage of a CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--disk-size-gb", type=int, required=True,
                        help="New size of attached disks (in GiB).",
                    )
                ],
                "resolver": clusters_expand_storage,
            },
            "set-suspended-state": {
                "help": "Suspend or resume a CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--value", type=lambda x: asbool(x),
                        required=True, help="The suspended status.",
                        choices=[True, False],
                    ),
                ],
                "resolver": clusters_set_suspended,
            },
            "set-product": {
                "help": "Change the cluster's product, which can be used to "
                        "change the compute (vCPU and RAM) of the cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--product-name", type=str, required=True,
                        help="The new product name to use. "
                             "Run ``croud products list --kind cluster`` to get "
                             "the list of available products.",
                    ),
                ],
                "resolver": clusters_set_product,
            },
            "set-backup-schedule": {
                "help": "Change the cluster's backup schedule.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--backup-hours", type=str, required=True,
                        help="A list of hours in UTC time that represent when backups "
                             "will take place along the day. The list must contain at "
                             "least one value and can have up to 24, comma-separated."
                    )
                ],
                "resolver": clusters_set_backup_schedule,
            },
            "snapshots": {
                "help": "View and restore snapshots (backups)",
                "commands": {
                    "list": {
                        "help": "List all snapshots of a cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The CrateDB cluster ID to use.",
                            ),
                            Argument(
                                "--days-ago", type=int, required=False, default=2,
                                help="Number of days to look back. "
                                     "(default: %(default)s)",
                            ),
                        ],
                        "resolver": clusters_snapshots_list,
                    },
                    "restore": {
                        "help": "Restore a snapshot of a cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The CrateDB cluster to restore "
                                     "the snapshot into.",
                            ),
                            Argument(
                                "--snapshot", type=str, required=True,
                                help="The snapshot to be restored.",
                            ),
                            Argument(
                                "--repository", type=str, required=True,
                                help="The repository that contains the snapshot to be "
                                     "restored.",
                            ),
                            Argument(
                                "--source-cluster-id", type=str, required=False,
                                help="The CrateDB cluster where the snapshot was "
                                     "created. It must belong to the same organization "
                                     "and region as the target cluster. If not "
                                     "specified, the ``--cluster-id`` will be used as "
                                     "both the source and the target.",
                            ),
                            Argument(
                                "--type", type=str, required=False,
                                choices=["all", "metadata", "tables", "sections"],
                                help="The type of data to be restored from the "
                                     "snapshot.",
                            ),
                            Argument(
                                "--tables", type=str, required=False,
                                help="The list of tables to restore, comma separated. "
                                     "Only valid together with ``--type tables``.",
                            ),
                            Argument(
                                "--sections", type=str, required=False,
                                help="The list of data sections to restore, comma "
                                     "separated. Only valid together with ``--type "
                                     "sections``. Valid sections are ``tables``, "
                                     "``views``, ``users``, ``privileges``, "
                                     "``analyzers`` or ``udfs``.",
                            ),
                        ],
                        "resolver": clusters_snapshots_restore,
                    },
                },
            },
            "subscription": {
                "help": "Manage subscription of a CrateDB cluster.",
                "commands": {
                    "update": {
                        "help": "Transfer a CrateDB cluster between subscriptions.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The CrateDB cluster ID to use.",
                            ),
                            Argument(
                                "--old-subscription-id", type=str, required=True,
                                help="The current subscription ID.",
                            ),
                            Argument(
                                "--new-subscription-id", type=str, required=True,
                                help="The ID of the subscription the cluster should be "
                                     "transferred to.",
                            ),
                        ],
                        "resolver": clusters_subscription_update,
                    },
                },
            },
            "import-jobs": {
                "help": "Manage data import into your CrateDB cluster.",
                "commands": {
                    "delete": {
                        "help": "Delete a data import job from the job history if it "
                                "has already finished. Otherwise, cancel the running "
                                "import job.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the import job belongs to."
                            ),
                            Argument(
                                "--import-job-id", type=str,
                                required=True,
                                help="The ID of the import job."
                            ),
                        ],
                        "resolver": import_jobs_delete,
                    },
                    "list": {
                        "help": "List all import jobs for a cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the import jobs belong to."
                            ),
                        ],
                        "resolver": import_jobs_list,
                    },
                    "create": {
                        "help": "Import data from a file.",
                        "commands" : {
                            "from-url": {
                                "help": "Create a data import job on the specified "
                                        "cluster from a url.",
                                "extra_args": [
                                    # Type URL params
                                    Argument(
                                        "--url", type=str, required=True,
                                        help="The URL the import file will be read "
                                             "from."
                                    ),
                                ] + import_job_create_common_args
                                  + import_job_create_common_file_args,
                                "resolver": import_jobs_create_from_url,
                            },
                            "from-file": {
                                "help": "Create a data import job from a local or "
                                        "uploaded file.",
                                "extra_args": [
                                    # Type file params
                                    Argument(
                                        "--file-id", type=str, required=False,
                                        help="The file ID that will be used for the "
                                             "import. If not specified then "
                                             "``--file-path`` must be specified. "
                                             "Please refer to `croud organizations "
                                             "files` for more info."
                                    ),
                                    Argument(
                                        "--file-path", type=str, required=False,
                                        help="The file in your local filesystem that "
                                             "will be used. If not specified then "
                                             "``--file-id`` must be specified. "
                                             "Please note the file will become visible "
                                             "under ``croud organizations files list``."
                                    ),
                                ] + import_job_create_common_args
                                  + import_job_create_common_file_args,
                                "resolver": import_jobs_create_from_file,
                            },
                            "from-s3": {
                                "help": "Create a data import job on the specified "
                                        "cluster from an Amazon S3 compatible "
                                        "location.",
                                "extra_args": [
                                    # Type S3 params
                                    Argument(
                                        "--bucket", type=str, required=True,
                                        help="The name of the S3 bucket that contains "
                                             "the file to be imported."
                                    ),
                                    Argument(
                                        "--file-path", type=str, required=True,
                                        help="The absolute path in the S3 bucket that "
                                             "points to the file to be imported. "
                                             "Globbing (use of *) is allowed."
                                    ),
                                    Argument(
                                        "--secret-id", type=str, required=True,
                                        help="The secret that contains the access key "
                                             "and secret key needed to access the file "
                                             "to be imported."
                                    ),
                                    Argument(
                                        "--endpoint", type=str, required=False,
                                        help="An Amazon S3 compatible endpoint."
                                    ),
                                ] + import_job_create_common_args
                                  + import_job_create_common_file_args,
                                "resolver": import_jobs_create_from_s3,
                            },
                            "from-dynamodb": {
                                "help": "Create a data import job on the specified "
                                        "cluster from an Amazon DynamoDB compatible "
                                        "location.",
                                "extra_args": [
                                    # Type S3 params
                                    Argument(
                                        "--ingestion-type", type=str,
                                        choices=[
                                            "IMPORT_ONLY",
                                            "IMPORT_AND_CDC",
                                            "CDC_ONLY"
                                        ],
                                        required=True,
                                        help="Determines how to ingest the data. "
                                             "IMPORT_ONLY will just ingest the data "
                                             "and finish. CDC_ONLY will continuously "
                                             "read CDC (Change Data Capture) events. "
                                             "IMPORT_AND_CDC will first import the "
                                             "data and then start listening for CDC "
                                             "events."
                                    ),
                                    Argument(
                                        "--aws-region", type=str, required=True,
                                        help="The name of the AWS region where the "
                                             "DynamoDB table is located."
                                    ),
                                    Argument(
                                        "--dynamodb-table", type=str, required=True,
                                        help="The name of the DynamoDB table."
                                    ),
                                    Argument(
                                        "--kinesis-stream-name", type=str,
                                        required=False,
                                        help="The name of the Kinesis Stream that will "
                                             "be used to read CDC events from. Only for"
                                             " CDC mode."
                                    ),
                                    Argument(
                                        "--secret-id", type=str, required=True,
                                        help="The secret that contains the access key "
                                             "and secret key needed to access the "
                                             "table to be imported."
                                    ),
                                    Argument(
                                        "--endpoint", type=str, required=False,
                                        help="An AWS DynamoDB compatible endpoint."
                                    ),
                                ] + import_job_create_common_args,
                                "resolver": import_jobs_create_from_dynamodb,
                            },
                            "from-azure-blob-storage": {
                                "help": "Create a data import job on the specified "
                                        "cluster from an Azure blob storage location.",
                                "extra_args": [
                                    # Type Azure Blob Storage params
                                    Argument(
                                        "--container-name", type=str,
                                        required=True,
                                        help="The name of the storage container "
                                             "where the file to be imported is located."
                                    ),
                                    Argument(
                                        "--blob-name", type=str, required=True,
                                        help="The absolute path in the storage "
                                             "container that points to the file to be "
                                             "imported. Globbing (use of *) is allowed."
                                    ),
                                    Argument(
                                        "--secret-id", type=str, required=True,
                                        help="The secret that contains the access key "
                                             "and secret key needed to access the file "
                                             "to be imported."
                                    ),
                                ] + import_job_create_common_args
                                  + import_job_create_common_file_args,
                                "resolver": import_jobs_create_from_azure_blob_storage,
                            },
                        },
                    },
                },
            },
            "export-jobs": {
                "help": "Manage data export from your CrateDB cluster into a file.",
                "commands": {
                    "delete": {
                        "help": "Delete a data export job from the job history if it "
                                "has already finished. Otherwise, cancel the running "
                                "export job.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the job belongs to."
                            ),
                            Argument(
                                "--export-job-id", type=str,
                                required=True,
                                help="The ID of the export job."
                            ),
                        ],
                        "resolver": export_jobs_delete,
                    },
                    "list": {
                        "help": "Lists all export jobs for a cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the export jobs belong to."
                            ),
                        ],
                        "resolver": export_jobs_list,
                    },
                    "create": {
                        "help": "Export data from a CrateDB cluster to a file. The "
                                "exported data can be downloaded from a URL once the "
                                "export job is completed or saved on your local "
                                "filesystem.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the data will be exported from."
                            ),
                            Argument(
                                "--table",
                                type=str,
                                required=True,
                                help="The table the data will be exported from.",
                            ),
                            Argument(
                                "--file-format",
                                type=str,
                                required=True,
                                choices=["csv", "json", "parquet"],
                                help="The format of the data in the file.",
                            ),
                            Argument(
                                "--compression",
                                type=str,
                                required=False,
                                choices=["gzip", "none"],
                                help="The compression method of the exported file.",
                            ),
                            Argument(
                                "--save-as",
                                type=str,
                                required=False,
                                help="The file on your local filesystem the data will "
                                     "be exported to. If not specified, you will "
                                     "receive the URL to download the file.",
                            ),
                        ],
                        "resolver": export_jobs_create,
                    },
                },
            },
            "scheduled-jobs": {
                "help": "Manage your scheduled sql jobs.",
                "commands": {
                    "create": {
                        "help": "Create a scheduled sql job to run at "
                                "specific times.",
                        "extra_args": [
                            Argument(
                                "--name", type=str, required=True,
                                help="Name of the sql job."
                            ),
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="Cluster where the job should be run."
                            ),
                            Argument(
                                "--cron", type=str, required=True,
                                help="Cron schedule of the sql job."
                            ),
                            Argument(
                                "--sql", type=str, required=True,
                                help="The sql statement the job should run."
                            ),
                            Argument(
                                "--enabled", type=str, required=True,
                                help="Enable or disable the job."
                            )
                        ],
                        "resolver": create_scheduled_job,
                    },
                    "list": {
                        "help": "List the scheduled sql jobs for a cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster of which jobs should be listed."
                            )
                        ],
                        "resolver": get_scheduled_jobs,
                    },
                    "logs": {
                        "help": "List the past executions of a scheduled sql job.",
                        "extra_args": [
                            Argument(
                                "--job-id", type=str, required=True,
                                help="The job id of the job log to be listed."
                            ),
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster of which the job log "
                                     "should be listed."
                            )
                        ],
                        "resolver": get_scheduled_job_log,
                    },
                    "delete": {
                        "help": "Delete specified scheduled sql job.",
                        "extra_args": [
                            Argument(
                                "--job-id", type=str, required=True,
                                help="The job id of the job to be deleted."
                            ),
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster of which the job "
                                     "should be deleted."
                            ),
                        ],
                        "resolver": delete_scheduled_job,
                    },
                    "edit": {
                        "help": "Edit specified scheduled sql job.",
                        "extra_args": [
                            Argument(
                                "--job-id", type=str, required=True,
                                help="The id of the job to edit."
                            ),
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster id where the job was created."
                            ),
                            Argument(
                                "--name", type=str, required=True,
                                help="The name of the sql job."
                            ),
                            Argument(
                                "--sql", type=str, required=True,
                                help="The sql statement of the sql job."
                            ),
                            Argument(
                                "--cron", type=str, required=True,
                                help="Cron schedule of the sql job."
                            ),
                            Argument(
                                "--enabled", type=str, required=True,
                                help="Enable or disable the sql job."
                            ),
                        ],
                        "resolver": edit_scheduled_job,
                    }
                }
            },
        },
    },
    "products": {
        "help": "Manage products. They represent the compute configuration and "
                "the scale and storage options that you can choose from when "
                "creating a cluster.",
        "commands": {
            "list": {
                "help": "List the available products for a region.",
                "extra_args": [
                    Argument(
                        "--kind", type=str, required=False, help="The product kind.",
                        choices=["cluster", "storage"]
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
            "get": {
                "help": (
                    "Get an organization by its ID."
                ),
                "extra_args": [
                    Argument(
                        "id", type=str,
                        help="The ID of the organization.",
                    ),
                ],
                "resolver": organizations_get,
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
                        help="The new support plan to use for the organization. "
                             "Argument is for superusers only.",
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
            "auditlogs": {
                "help": "Show audit logs for an organization.",
                "commands": {
                    "list": {
                        "help": "List all audit events in the current organization.",
                        "extra_args": [
                            Argument(
                                "--action", type=str, required=False,
                                help="The audit event action.",
                            ),
                            Argument(
                                "--from", type=str, required=False, dest="from_",
                                help="Only show events from this point in time.",
                                metavar="FROM",
                            ),
                            Argument(
                                "--to", type=str, required=False,
                                help="Only show events older than this.",
                            ),
                            Argument(
                                "--org-id", type=str, required=False,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": auditlogs_list,
                    },
                },
            },
            "users": {
                "help": "Manage users in an organization.",
                "commands": {
                    "add": {
                        "help": "Add a user to an organization.",
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
                        "help": "List all users that are admins or members of an "
                                "organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=False,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": org_users_list,
                    },
                    "remove": {
                        "help": "Remove a user from an organization.",
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
            "secrets": {
                "help": "Manage organization's secrets.",
                "commands" : {
                    "list": {
                        "help": "Lists all the secrets that belong to an organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": org_secrets_list,
                    },
                    "create": {
                        "help": "Creates a new secret for the given organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--name", type=str, required=True,
                                help="The name the secret will be known as.",
                            ),
                            Argument(
                                "--type", type=str, required=True,
                                choices=["AWS", "AZURE", "MONGODB"],
                                help="The type of Secret. Either AWS, Azure, or "
                                     "MongoDB.",
                            ),
                            # AWS arguments
                            Argument(
                                "--access-key", type=str, required=False,
                                help="For an AWS type secret, the access key ID.",
                            ),
                            Argument(
                                "--secret-key", type=str, required=False,
                                help="For an AWS type secret, the secret key.",
                            ),
                            # Azure/MongoDB arguments
                            Argument(
                                "--connection-string", type=str, required=False,
                                help="For an Azure or MongoDB type secret, the "
                                     "connection string or URL that grants access to "
                                     "a resource.",
                            ),
                            # MongoDB arguments
                            Argument(
                                "--username", type=str, required=False,
                                help="For a MongoDB type secret, the username. It "
                                     "requires the password as well and it cannot be "
                                     "set if the certificate is provided.",
                            ),
                            Argument(
                                "--password", type=str, required=False,
                                help="For a MongoDB type secret, the password. It "
                                     "requires the username as well and it cannot be "
                                     "set if the certificate is provided.",
                            ),
                            Argument(
                                "--certificate", type=str, required=False,
                                help="For a MongoDB type secret, the certificate. It "
                                     "cannot be set if the username and password are "
                                     "provided.",
                            ),
                        ],
                        "resolver": org_secrets_create,
                    },
                    "delete": {
                        "help": "Delete a secret from an organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--secret-id", type=str, required=True,
                                help="The secret ID to use.",
                            ),
                        ],
                        "resolver": org_secrets_delete,
                    },
                }
            },
            "files": {
                "help": "Manage organization's uploaded files. The files can then be "
                        "used as data sources for data import jobs.",
                "commands": {
                    "get": {
                        "help": "Get the details of a file uploaded to an "
                                "organization, including a pre-signed URL for "
                                "downloading the file.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--file-id", type=str, required=True,
                                help="The ID of the file.",
                            ),
                        ],
                        "resolver": org_files_get,
                    },
                    "list": {
                        "help": "List all files uploaded to this organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                        ],
                        "resolver": org_files_list,
                    },
                    "create": {
                        "help": "Upload a new file to the organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--file-path", type=str, required=True,
                                help="The local file to be uploaded.",
                            ),
                            Argument(
                                "--name", type=str, required=False,
                                help="The name that will be displayed when listing the "
                                     "file. If not provided, the file name will be "
                                     "used.",
                            ),
                        ],
                        "resolver": org_files_create,
                    },
                    "delete": {
                        "help": "Delete a file uploaded to an organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--file-id", type=str, required=True,
                                help="The ID of the file.",
                            ),
                        ],
                        "resolver": org_files_delete,
                    },
                }
            },
            "credits": {
                "help": "Manage organization's credits.",
                "commands" : {
                    "list": {
                        "help": "List all credits of an organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--status", type=str, required=False,
                                help="Filter credits by status, comma separated. Valid "
                                     "values are ``ACTIVE`` and ``EXPIRED``. By "
                                     "default only ``ACTIVE`` credits are listed.",
                            ),
                        ],
                        "resolver": org_credits_list,
                    },
                    "create": {
                        "help": "Create a new credit for an organization.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--amount", type=float, required=True,
                                help="The amount to be credited in USD.",
                            ),
                            Argument(
                                "--expiration-date", type=str, required=True,
                                help="The expiration date of the credit in ISO 8601 "
                                     "format (i.e. ``2024-01-01T10:00:00Z``).",
                            ),
                            Argument(
                                "--comment", type=str, required=True,
                                help="The reason for creating this credit.",
                            ),
                        ],
                        "resolver": org_credits_create,
                    },
                    "edit": {
                        "help": "Edit the specified credit.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--credit-id", type=str, required=True,
                                help="The credit ID to use.",
                            ),
                            Argument(
                                "--amount", type=float, required=False,
                                help="The amount to be credited in USD. It can only be "
                                     "increased.",
                            ),
                            Argument(
                                "--expiration-date", type=str, required=False,
                                help="The expiration date of the credit in ISO 8601 "
                                     "format (i.e. ``2024-01-01T10:00:00Z``).",
                            ),
                            Argument(
                                "--comment", type=str, required=False,
                                help="The reason for creating this credit.",
                            ),
                        ],
                        "resolver": org_credits_edit,
                    },
                    "expire": {
                        "help": "Expire a credit, making it unusable for paying for "
                                "CrateDB Cloud resources.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--credit-id", type=str, required=True,
                                help="The credit ID to use.",
                            ),
                        ],
                        "resolver": org_credits_expire,
                    },
                }
            },
            "customer": {
                "help": "Manage organization's customer information."
                        "This includes the billing information",
                "commands" : {
                    "get": {
                        "help": "Get the customer information for an organization."
                                "This includes the billing information"
                                ".",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            )
                        ],
                        "resolver": org_customer_get,
                    },
                    "edit": {
                        "help": "Edits the organization's customer information.",
                        "extra_args": [
                            Argument(
                                "--org-id", type=str, required=True,
                                help="The organization ID to use.",
                            ),
                            Argument(
                                "--name", type=str, required=True,
                                help="The organization name.",
                            ),
                            Argument(
                                "--email", type=str, required=True,
                                help="The customer's email.",
                            ),
                            Argument(
                                "--phone", type=str, required=True,
                                help="The customer's phone number.",
                            ),
                            Argument(
                                "--country", type=str, required=True,
                                help="Billing address: country.",
                            ),
                            Argument(
                                "--city", type=str, required=True,
                                help="Billing address: city.",
                            ),
                            Argument(
                                "--line1", type=str, required=True,
                                help="Billing address: line 1.",
                            ),
                            Argument(
                                "--line2", type=str, required=False,
                                help="Billing address: line 2.",
                            ),
                            Argument(
                                "--postal-code", type=str, required=True,
                                help="Billing address: postal code.",
                            ),
                            Argument(
                                "--tax-id", type=str, required=False,
                                help="The customer's tax ID.",
                            ),
                            Argument(
                                "--tax-id-type", type=str, required=False,
                                help="The customer's tax ID type, e.g. 'eu_vat'.",
                            )
                        ],
                        "resolver": org_customer_edit,
                    }
                }
            }
        },
    },
    "users": {
        "help": "Manage users.",
        "commands": {
            "list": {
                "help": "List all users. The command is for superusers only.",
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
            "delete": {
                "help": "Delete the specified user. The command is for "
                        "superusers only.",
                "extra_args": [
                    Argument(
                        "--user-id", type=str, required=True,
                        help="The user ID to use.",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False)
                ],
                "resolver": users_delete,
            },
        },
    },
    "api-keys": {
        "help": "Manage your own API keys.",
        "commands": {
            "list": {
                "help": "List all the API keys that belong to the current user.",
                "resolver": api_keys_list,
            },
            "create": {
                "help": "Create a new API key for your user. It will have the same "
                        "permissions as your user.",
                "resolver": api_keys_create,
            },
            "delete": {
                "help": "Delete the API key specified that belongs to your user.",
                "resolver": api_keys_delete,
                "extra_args": [
                    Argument(
                        "--api-key", type=str, required=True,
                        help="The key that identifies an API key that belongs to your "
                             "user.",
                    ),
                ]
            },
            "edit": {
                "help": "Allow activating or deactivating an existing API key",
                "resolver": api_keys_edit,
                "extra_args": [
                    Argument(
                        "--api-key", type=str, required=True,
                        help="The key that identifies an API key that belongs to your "
                             "user.",
                    ),
                    Argument(
                        "--active", type=str, required=True,
                        choices=["true", "false"],
                        help="Either true or false. Determines whether the API key can "
                             "be used or not.",
                    ),
                ]
            },
        },
    },
    "regions": {
        "help": "Print information about available regions.",
        "commands": {
            "list": {
                "help": "List all available regions.",
                "extra_args": [
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": regions_list,
            },
            "create": {
                "help": "Create a new Edge region. The feature is not maintained "
                        "and we don't recommend using it.",
                "resolver": regions_create,
                "extra_args": [
                    Argument(
                        "--aws-bucket", type=str, required=False,
                        help="The AWS S3 bucket where cluster backups will be stored.",
                    ),
                    Argument(
                        "--aws-region", type=str, required=False,
                        help="The AWS region where the S3 bucket for cluster"
                             " backups is expected to be.",
                    ),
                    Argument(
                        "--description", type=str, required=True,
                        help="The description of the new region.",
                    ),
                    Argument(
                        "--org-id", type=str, required=True,
                        help="The organization ID to use.",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False),
                ],
            },
            "delete": {
                "help": "Delete an existing Edge region. The feature is not maintained "
                        "and we don't recommend using it.",
                "resolver": regions_delete,
                "extra_args": [
                    Argument(
                        "--name", type=str, required=True,
                        help="The name of the region that will be deleted."
                    ),
                    Argument("-y", "--yes", action="store_true", default=False),
                ],
            },
        }
    },
    "subscriptions": {
        "help": "Manage subscriptions. Subscriptions are the configured payment "
                "methods for an organization.",
        "commands": {
            "create": {
                "help": ("Create a subscription in the specified organization. Command "
                         "is for superusers only."),
                "extra_args": [
                    Argument(
                        "--type", type=str, required=True,
                        choices=['contract'],
                        help="The subscription type to use.",
                    ),
                    Argument(
                        "--org-id", type=str, required=True,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": subscriptions_create,
            },
            "get": {
                "help": (
                    "Get a subscription by its ID."
                ),
                "extra_args": [
                    Argument(
                        "id", type=str,
                        help="The ID of the subscription.",
                    ),
                ],
                "resolver": subscriptions_get,
            },
            "delete": {
                "help": "Cancel a Stripe or contract subscription. "
                        "CAVEAT EMPTOR! "
                        "This will delete any clusters running in this subscription.",
                "extra_args": [
                    Argument(
                        "--subscription-id", type=str, required=True,
                        help="The ID of the subscription.",
                    ),
                    Argument("-y", "--yes", action="store_true", default=False),
                ],
                "resolver": subscription_delete,
            },
            "list": {
                "help": "List all subscriptions the current user has access to.",
                "extra_args": [
                    Argument(
                        "--org-id", type=str, required=False,
                        help="The organization ID to use.",
                    ),
                ],
                "resolver": subscriptions_list,
            },
        },
    },
    "cloud-configurations": {
        "help": "Manage configurations of CrateDB Cloud. This command is for "
                "superusers only.",
        "commands": {
            "set": {
                "help": (
                    "Set a configuration value either globally or for a single "
                    "organization or user only. This command is for superusers only."
                ),
                "extra_args": [
                    Argument(
                        "--key", type=str, required=True,
                        help="The configuration key to set.",
                    ),
                    Argument(
                        "--value", type=str, required=True,
                        help="The configuration value to use.",
                    ),
                    Argument(
                        "--org-id", type=str, required=False,
                        help="Override the value for a single organization only.",
                    ),
                    Argument(
                        "--user-id", type=str, required=False,
                        help="Override the value for a single user only.",
                    ),
                ],
                "resolver": cloud_configurations_set,
            },
            "get": {
                "help": (
                    "Get a single configuration value by its key. "
                    "This command is for superusers only."
                ),
                "extra_args": [
                    Argument(
                        "--key", type=str, required=True,
                        help="The configuration key to get.",
                    ),
                    Argument(
                        "--org-id", type=str, required=False,
                        help="Optionally get the value for a certain organization. "
                             "Defaults to the global configuration value.",
                    ),
                    Argument(
                        "--user-id", type=str, required=False,
                        help="Optionally get the value for a certain user. "
                             "Defaults to the global configuration value.",
                    ),
                ],
                "resolver": cloud_configurations_get,
            },
            "list": {
                "help": (
                    "List all CrateDB Cloud configurations. This command "
                    "is for superusers only."
                ),
                "extra_args": [
                    Argument(
                        "--org-id", type=str, required=False,
                        help="Optionally get the values for a certain organization. "
                             "Defaults to the global configuration values.",
                    ),
                    Argument(
                        "--user-id", type=str, required=False,
                        help="Optionally get the values for a certain user. "
                             "Defaults to the global configuration values.",
                    ),
                ],
                "resolver": cloud_configurations_list,
            }
        },
    }
}
# fmt: on


def get_parser():
    tree = {
        "help": "A command line interface for CrateDB Cloud. More information about "
        "CrateDB Cloud CLI can be found at "
        "https://cratedb.com/docs/cloud/cli/en/latest/.",
        "commands": command_tree,
    }
    return create_parser(tree)


def main():
    if not CONFIG.is_valid():
        print_error(
            "Your configuration file is incompatible with the current version of croud."
        )
        print_info(
            f"Please delete the file '{CONFIG._file_path}' or update it manually."
        )
        sys.exit(1)

    colorama.init()

    parser = get_parser()
    shtab.add_argument_to(parser)  # Tab completion stuff
    params = parser.parse_args(sys.argv[1:])
    if "resolver" in params:
        fn = params.resolver
        del params.resolver
        with HALO:
            fn(params)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
