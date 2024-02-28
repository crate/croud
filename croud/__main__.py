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
from distutils.util import strtobool

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
    clusters_upgrade,
    create_scheduled_job,
    delete_scheduled_job,
    edit_scheduled_job,
    export_jobs_create,
    export_jobs_delete,
    export_jobs_list,
    get_scheduled_job_log,
    get_scheduled_jobs,
    import_job_progress,
    import_jobs_create_from_azure_blob_storage,
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

# Arguments common to all import-job create commands
import_job_create_common_args = [
    Argument(
        "--cluster-id",
        type=str,
        required=True,
        help="The cluster the data will be imported into.",
    ),
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
        choices=["gzip"],
        help="The compression method the file uses.",
    ),
    Argument(
        "--table",
        type=str,
        required=True,
        help="The table the data will be imported into.",
    ),
    Argument(
        "--create-table",
        type=lambda x: bool(strtobool(str(x))),  # noqa
        required=False,
        help="Whether the table should be created automatically"
        " if it does not exist. If true new columns will also be added when the data"
        " requires them.",
    ),
    Argument(
        "--transformations",
        type=str,
        required=False,
        help="The transformations to apply when fetching data. This is the SELECT "
        "statement from an SQL query that is executed on the internal DuckDB "
        "database that the data is loaded to before inserting into CrateDB. "
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
                "help": "Edit your user data.",
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
        "help": "Log in to CrateDB Cloud.",
        "resolver": login,
        "extra_args": [
            Argument(
                "--idp", type=str, required=True,
                choices=["cognito", "azuread", "github", "google"],
                help="The identity provider (IdP) for the login."
            ),
        ],
    },
    "logout": {"help": "Log out of CrateDB Cloud.", "resolver": logout},
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
                        "help": "Set the current profile.",
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
                        "help": "Add a new profile.",
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
                        "help": "Remove an existing profile.",
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
                    Argument(
                        "--backup-location-type",
                        choices=["s3"],
                        type=str,
                        required=False,
                        help="The type of the custom backup location to use. "
                             "Only 's3' currently supported. "
                             "CrateDB Edge regions only."
                    ),
                    Argument(
                        "--backup-location", type=str, required=False,
                        help="The location of where backups are to be stored, "
                             "i.e. name of s3 bucket for s3 locations. "
                             "CrateDB Edge regions only."
                    ),
                    Argument(
                        "--backup-location-access-key-id", type=str, required=False,
                        help="The AWS access key id for the given s3 bucket. "
                             "CrateDB Edge regions only."
                    ),
                    Argument(
                        "--backup-location-endpoint-url", type=str, required=False,
                        help="The URL to a S3 compatible endpoint. "
                             "CrateDB Edge regions only."
                    ),
                    Argument(
                        "--backup-location-secret-access-key", type=str, required=False,
                        help="The AWS secret access key for the given s3 bucket. "
                             "CrateDB Edge regions only."
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
                "help": "Edit the specified project.",
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
                    "the specified region."
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
                        help="The project ID to use.",
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
                        "-p", "--project-id", type=str,
                        required=False,
                        help="The project ID to use.",
                    ),
                    Argument(
                        "--org-id", type=str,
                        required=False,
                        help="The organization ID to use.",
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
                        help="The CrateDB password to use. Minimum 24 characters.",
                    ),
                    Argument(
                        "--subscription-id", type=str, required=True,
                        help="The subscription to use for billing of this cluster.",
                    ),
                    Argument(
                        "--channel", type=str, default="stable", required=False,
                        choices=["stable", "testing", "nightly"],
                        help="The channel of the CrateDB version.",
                    ),
                    Argument(
                        "--cpus", type=float, required=False,
                        help="Number of CPU cores to allocate. Can be fractional. "
                             "CrateDB Edge regions only.",
                    ),
                    Argument(
                        "--disks", type=int, required=False,
                        help="Number of disks to attach. "
                             "CrateDB Edge regions only.",
                    ),
                    Argument(
                        "--disk-size-gb", type=int, required=False,
                        help="Size of disks to attach (in GiB).",
                    ),
                    Argument(
                        "--disk-type", type=str, required=False,
                        choices=["standard", "premium"],
                        help="Type of disks to use. "
                             "CrateDB Edge regions only.",
                    ),
                    Argument(
                        "--memory-size-mb", type=int, required=False,
                        help="Amount of memory to allocate (in MiB). "
                             "CrateDB Edge regions only.",
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
                "help": "Set the deletion protection status of a CrateDB cluster.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--value", type=lambda x: bool(strtobool(str(x))),
                        required=True, help="The deletion protection status",
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
                        "--value", type=lambda x: bool(strtobool(str(x))),
                        required=True, help="The suspended status.",
                    ),
                ],
                "resolver": clusters_set_suspended,
            },
            "set-product": {
                "help": "Change the cluster's product.",
                "extra_args": [
                    Argument(
                        "--cluster-id", type=str, required=True,
                        help="The CrateDB cluster ID to use.",
                    ),
                    Argument(
                        "--product-name", type=str, required=True,
                        help="The new product name to use."
                    )
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
                "help": "View and restore snapshots",
                "commands": {
                    "list": {
                        "help": "List the cluster snapshots available.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The CrateDB cluster ID to use.",
                            ),
                            Argument(
                                "--days-ago", type=int, required=False, default=2,
                                help="Number of days to look back.",
                            ),
                        ],
                        "resolver": clusters_snapshots_list,
                    },
                    "restore": {
                        "help": "Restore the specified snapshot.",
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
                                help="The CrateDB cluster ID of the snapshot to be "
                                     "used belongs to. Must belong to the same "
                                     "organization as the target cluster. "
                                     "If not specified the ``--cluster-id`` CrateDB"
                                     " cluster will be used as the source.",
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
            "import-jobs": {
                "help": "Manage data import jobs.",
                "commands": {
                    "delete": {
                        "help": "Cancels an already running data import job that has "
                                "not finished yet. "
                                "If the job has already finished it deletes it from "
                                "the job history.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the import job belongs to."
                            ),
                            Argument(
                                "--import-job-id", type=str,
                                required=True,
                                help="The ID of the Import Job."
                            ),
                        ],
                        "resolver": import_jobs_delete,
                    },
                    "list": {
                        "help": "Lists data import jobs that belong to a specific "
                                "cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the import jobs belong to."
                            ),
                        ],
                        "resolver": import_jobs_list,
                    },
                    "create": {
                        "help": "Create a data import job for the specified cluster.",
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
                                ] + import_job_create_common_args,
                                "resolver": import_jobs_create_from_url,
                            },
                            "from-file": {
                                "help": "Create a data import job on the specified "
                                        "cluster from a file.",
                                "extra_args": [
                                    # Type file params
                                    Argument(
                                        "--file-id", type=str, required=False,
                                        help="The file ID that will be used for the "
                                             "import. If not specified then --file-path"
                                             " must be specified. "
                                             "Please refer to `croud organizations "
                                             "files` for more info."
                                    ),
                                    Argument(
                                        "--file-path", type=str, required=False,
                                        help="The file in your local filesystem that "
                                             "will be used. If not specified then "
                                             "--file-id must be specified. "
                                             "Please note the file will become visible "
                                             "under `croud organizations files list`."
                                    ),
                                ] + import_job_create_common_args,
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
                                ] + import_job_create_common_args,
                                "resolver": import_jobs_create_from_s3,
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
                                ] + import_job_create_common_args,
                                "resolver": import_jobs_create_from_azure_blob_storage,
                            },
                        },
                    },
                    "progress": {
                        "help": "Shows the progress of an import job.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the import jobs belong to."
                            ),
                            Argument(
                                "--import-job-id", type=str,
                                required=True,
                                help="The ID of the Import Job."
                            ),
                            Argument(
                                "--limit", type=str, required=False,
                                help="The number of files returned."
                                     "Use keywork 'ALL' to have no limit applied."
                            ),
                            Argument(
                                "--offset", type=int, required=False,
                                help="The offset to skip before beginning to "
                                     "return the files."
                            ),
                            Argument(
                                "--summary", type=lambda x: bool(strtobool(str(x))),
                                required=False,
                                help="Show only global progress."
                            ),
                        ],
                        "resolver": import_job_progress,
                    },
                },
            },
            "export-jobs": {
                "help": "Manage data export jobs.",
                "commands": {
                    "delete": {
                        "help": "Cancels an already running data export job that has "
                                "not finished yet. "
                                "If the job has already finished it deletes it from "
                                "the job history.",
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
                        "help": "Lists data export jobs that belong to a specific "
                                "cluster.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster the export jobs belong to."
                            ),
                        ],
                        "resolver": export_jobs_list,
                    },
                    "create": {
                        "help": "Create a data export job for the specified cluster.",
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
                                choices=["gzip"],
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
                        "help": "Get all scheduled sql jobs.",
                        "extra_args": [
                            Argument(
                                "--cluster-id", type=str, required=True,
                                help="The cluster of which jobs should be listed."
                            )
                        ],
                        "resolver": get_scheduled_jobs,
                    },
                    "logs": {
                        "help": "Logs of a scheduled sql job.",
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
                                choices=["AWS", "AZURE"],
                                help="The type of Secret. Either AWS or Azure.",
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
                            # Azure arguments
                            Argument(
                                "--connection-string", type=str, required=False,
                                help="For an Azure type secret, the connection string "
                                     "or URL that grants access to a resource.",
                            ),
                        ],
                        "resolver": org_secrets_create,
                    },
                    "delete": {
                        "help": "Deletes the secret that matches the given ID for the "
                                "organization specified.",
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
                "help": "Manage organization's files.",
                "commands": {
                    "get": {
                        "help": (
                            "Get a file by its ID."
                        ),
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
                        "help": "Uploads a new file to the organization.",
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
                        "help": "Deletes a previously uploaded file.",
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
                        "help": "Lists all credits of an organization.",
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
                        "help": "Creates a new credit for the specified organization.",
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
                        "help": "Edits the specified credit.",
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
                        "help": "Expires the specified credit.",
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
            }
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
                "help": "List all the API keys that belong to you.",
                "resolver": api_keys_list,
            },
            "create": {
                "help": "Create a new API key for your user. It will have the same "
                        "permissions as your user.",
                "resolver": api_keys_create,
            },
            "delete": {
                "help": "Deletes the API key specified that belongs to your user.",
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
                "help": "Edit the API key specified that belongs to your user, "
                        "allowing you to activate or deactivate it.",
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
                "help": "Create a new region.",
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
                "help": "Delete an existing edge region.",
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
        "help": "Manage subscriptions.",
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
                "help": "For Stripe or contract subscriptions only. Cancels the "
                        "specified subscription. "
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
        "help": "Manage configurations of CrateDB Cloud.",
        "commands": {
            "set": {
                "help": (
                    "Set a configuration key/value. This command "
                    "is for superusers only."
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
                ],
                "resolver": cloud_configurations_set,
            },
            "get": {
                "help": (
                    "Get the configuration value by its key. This command "
                    "is for superusers only."
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
                ],
                "resolver": cloud_configurations_get,
            },
            "list": {
                "help": (
                    "List all cloud configurations. This command "
                    "is for superusers only."
                ),
                "extra_args": [
                    Argument(
                        "--org-id", type=str, required=False,
                        help="Optionally get the values for a certain organization. "
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
        "help": "A command line interface for CrateDB Cloud.",
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
