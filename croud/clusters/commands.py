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
import functools
import pathlib
import time
from argparse import Namespace
from datetime import datetime, timedelta, timezone
from shutil import copyfileobj
from typing import Any, Dict, Optional, cast

import bitmath
import requests
from tqdm.auto import tqdm
from yarl import URL

from croud.api import Client
from croud.clusters.exceptions import AsyncOperationNotFound
from croud.config import CONFIG, get_output_format
from croud.organizations.commands import op_upload_file_to_org
from croud.printer import print_error, print_info, print_response, print_success
from croud.tools.spinner import HALO
from croud.util import grand_central_jwt_token, require_confirmation


def clusters_get(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/clusters/{args.id}/")
    print_response(
        data=data,
        errors=errors,
        output_fmt=get_output_format(args),
    )


def clusters_list(args: Namespace) -> None:
    if args.org_id:
        url = f"/api/v2/organizations/{args.org_id}/clusters/"
    else:
        url = "/api/v2/clusters/"

    params = {}
    if args.project_id:
        params["project_id"] = args.project_id

    client = Client.from_args(args)
    data, errors = client.get(url, params=params)
    print_response(
        data=data,
        errors=errors,
        keys=[
            "id",
            "name",
            "num_nodes",
            "crate_version",
            "project_id",
            "username",
            "suspended",
            "fqdn",
            "channel",
        ],
        output_fmt=get_output_format(args),
    )


def clusters_deploy(args: Namespace) -> None:
    if not args.project_id and not (args.org_id and args.region):
        # We cannot have dynamically required params in croud, so have to verify here.
        print_error("Either a project id or organization id and region are required.")
        return

    body = {
        "cluster": {
            "crate_version": args.version,
            "name": args.cluster_name,
            "password": args.password,
            "product_name": args.product_name,
            "product_tier": args.tier,
            "username": args.username,
            "channel": args.channel,
        },
        "subscription_id": args.subscription_id,
    }
    if args.project_id:
        body["project_id"] = args.project_id
    else:
        body["project"] = {"name": args.cluster_name, "region": args.region}

    if args.unit:
        body["cluster"]["product_unit"] = args.unit
    _handle_edge_params(body["cluster"], args)

    client = Client.from_args(args)

    org_id = args.org_id or _lookup_organization_id_for_project(
        client, args, args.project_id
    )
    if not org_id:
        return

    data, errors = client.post(f"/api/v2/organizations/{org_id}/clusters/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "fqdn", "url"],
        output_fmt=get_output_format(args),
    )

    if errors or not data:
        return

    print_info("Cluster creation initiated. It may take a few minutes to complete.")

    _wait_for_completed_operation(
        client=client,
        cluster_id=data["id"],
        request_params={"type": "CREATE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{data['id']}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "fqdn", "url"],
        output_fmt=get_output_format(args),
    )


def clusters_scale(args: Namespace) -> None:
    body = {"product_unit": args.unit}
    client = Client.from_args(args)
    data, errors = client.put(f"/api/v2/clusters/{args.cluster_id}/scale/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "num_nodes"],
        output_fmt=get_output_format(args),
    )

    if errors:
        return

    print_info(
        "Cluster scaling initiated. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "SCALE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "num_nodes"],
        output_fmt=get_output_format(args),
    )


def import_jobs_create_from_url(args: Namespace) -> None:
    extra_body = {
        "url": {
            "url": args.url,
        }
    }
    args.type = "url"
    import_jobs_create(args, extra_payload=extra_body)


def import_jobs_create_from_s3(args: Namespace) -> None:
    extra_body = {
        "s3": {
            "bucket": args.bucket,
            "file_path": args.file_path,
            "secret_id": args.secret_id,
        }
    }
    if args.endpoint:
        extra_body["s3"]["endpoint"] = args.endpoint
    args.type = "s3"
    import_jobs_create(args, extra_payload=extra_body)


def import_jobs_create_from_azure_blob_storage(args: Namespace) -> None:
    extra_body = {
        "azureblob": {
            "container_name": args.container_name,
            "blob_name": args.blob_name,
            "secret_id": args.secret_id,
        }
    }
    args.type = "azureblob"
    import_jobs_create(args, extra_payload=extra_body)


def _get_org_id_from_cluster_id(client, cluster_id: str) -> Optional[str]:
    data, errors = client.get(f"/api/v2/clusters/{cluster_id}/")
    if errors or not data:
        return None

    project_id = data["project_id"]

    data, errors = client.get(f"/api/v2/projects/{project_id}/")
    if errors or not data:
        return None

    return data["organization_id"]


def import_jobs_create_from_file(args: Namespace) -> None:
    file_id = args.file_id

    if not args.file_path and not args.file_id:
        print_error("Please specify either --file-id or --file-path")
        return

    if args.file_path:
        client = Client.from_args(args)
        org_id = _get_org_id_from_cluster_id(client, args.cluster_id)
        if not org_id:
            print_error("Could not find the organization related to the cluster.")
            return

        data, errors = op_upload_file_to_org(client, org_id, args.file_path)
        if errors or not data:
            print_error("Aborted import job creation.")
            return
        file_id = data["id"]

    extra_body = {
        "file": {
            "id": file_id,
        }
    }
    args.type = "file"
    import_jobs_create(args, extra_payload=extra_body)


def import_jobs_create(args: Namespace, extra_payload: Dict[str, Any]) -> None:
    body = {
        "type": args.type,
        "format": args.file_format,
        "destination": {
            "table": args.table,
        },
    }

    if args.compression:
        body["compression"] = args.compression

    if args.create_table is not None:
        body["destination"]["create_table"] = args.create_table

    if args.transformations:
        body["schema"] = {"select": args.transformations}

    if extra_payload:
        body.update(extra_payload)

    client = Client.from_args(args)
    data, errors = client.post(
        f"/api/v2/clusters/{args.cluster_id}/import-jobs/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "cluster_id", "status"],
        output_fmt=get_output_format(args),
    )

    if data:
        import_job_id = data["id"]

        _wait_for_completed_operation(
            client=client,
            cluster_id=args.cluster_id,
            request_params={"import_job_id": import_job_id},
            operation_status_func=_get_import_job_operation_status,
            feedback_func=(
                _data_job_feedback_func,
                ("import",),
            ),
        )


def import_jobs_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(
        f"/api/v2/clusters/{args.cluster_id}/import-jobs/{args.import_job_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "cluster_id", "status"],
        output_fmt=get_output_format(args),
    )


def import_jobs_list(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/import-jobs/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "cluster_id", "status", "type", "destination"],
        output_fmt=get_output_format(args),
        transforms={
            "destination": lambda field: field.get("table"),
        },
    )


def import_job_progress(args: Namespace) -> None:
    client = Client.from_args(args)

    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.offset:
        params["offset"] = args.offset

    url = (
        f"/api/v2/clusters/{args.cluster_id}/import-jobs/{args.import_job_id}/progress/"
    )
    data, errors = client.get(url, params=params)

    if args.summary:
        print_response(
            data=data.get("progress", {}) if data else {},
            errors=errors,
            keys=[
                "percent",
                "records",
                "failed_records",
                "total_records",
                "total_files",
            ],
            output_fmt=get_output_format(args),
        )
    else:
        print_response(
            data=data.get("progress", {}).get("files", []) if data else {},
            errors=errors,
            keys=[
                "name",
                "percent",
                "records",
                "failed_records",
                "total_records",
            ],
            output_fmt=get_output_format(args),
        )


def clusters_upgrade(args: Namespace) -> None:
    body = {"crate_version": args.version}
    client = Client.from_args(args)
    data, errors = client.put(f"/api/v2/clusters/{args.cluster_id}/upgrade/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "crate_version"],
        output_fmt=get_output_format(args),
    )

    if errors:
        return

    print_info(
        "Cluster upgrade initiated. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "UPGRADE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "crate_version"],
        output_fmt=get_output_format(args),
    )


@require_confirmation(
    "Are you sure you want to delete the cluster?",
    cancel_msg="Cluster deletion cancelled.",
)
def clusters_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        success_message="Cluster deleted.",
        output_fmt=get_output_format(args),
    )


def clusters_restart_node(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(
        f"/api/v2/clusters/{args.cluster_id}/nodes/{args.ordinal}"
    )
    print_response(
        data=data,
        errors=errors,
        keys=["code", "status"],
        success_message=(
            "Node restarted. It may take a few minutes to complete the changes."
        ),
        output_fmt=get_output_format(args),
    )


def clusters_set_deletion_protection(args: Namespace) -> None:
    body = {"deletion_protected": args.value}
    client = Client.from_args(args)
    data, errors = client.put(
        f"/api/v2/clusters/{args.cluster_id}/deletion-protection/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "deletion_protected"],
        success_message=("Cluster deletion protection status successfully updated"),
        output_fmt=get_output_format(args),
    )


def clusters_set_suspended(args: Namespace) -> None:
    body = {"suspended": args.value}
    client = Client.from_args(args)
    data, errors = client.put(f"/api/v2/clusters/{args.cluster_id}/suspend/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "suspended"],
        output_fmt=get_output_format(args),
    )

    if errors:
        return
    print_info(
        "Updating the cluster status initiated. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "SUSPEND", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "suspended"],
        output_fmt=get_output_format(args),
    )


@require_confirmation("This will overwrite all existing CIDR restrictions. Continue?")
def clusters_set_ip_whitelist(args: Namespace) -> None:
    networks = args.net
    networks = networks.split(",")
    cidr = []

    for net in networks:
        if len(net) > 0:
            cidr.append({"cidr": net})

    body = {"ip_whitelist": cidr}

    client = Client.from_args(args)
    data, errors = client.put(
        f"/api/v2/clusters/{args.cluster_id}/ip-restrictions/", body=body
    )  # type: ignore
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "ip_whitelist"],
        output_fmt=get_output_format(args),
    )

    if errors:
        return
    print_info(
        "Updating the IP Network whitelist initiated. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "ALLOWED_CIDR_UPDATE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "ip_whitelist"],
        output_fmt=get_output_format(args),
    )


def _disk_size_transform(field):
    disk_size = str(bitmath.Byte(field["disk_size_per_node_bytes"]).best_prefix())
    return f"Disk size: {disk_size}"


def clusters_expand_storage(args: Namespace) -> None:
    body = {
        "disk_size_per_node_bytes": args.disk_size_gb * 1024 * 1024 * 1024,
    }

    client = Client.from_args(args)
    data, errors = client.put(
        f"/api/v2/clusters/{args.cluster_id}/storage/", body=body
    )  # type: ignore
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "hardware_specs"],
        output_fmt=get_output_format(args),
        transforms={"hardware_specs": _disk_size_transform},
    )

    if errors:
        return
    print_info(
        "Cluster storage expansion initiated. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "EXPAND_STORAGE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "hardware_specs"],
        output_fmt=get_output_format(args),
        transforms={"hardware_specs": _disk_size_transform},
    )


def clusters_set_product(args: Namespace) -> None:
    body = {
        "product_name": args.product_name,
    }

    client = Client.from_args(args)
    data, errors = client.put(
        f"/api/v2/clusters/{args.cluster_id}/product/", body=body
    )  # type: ignore
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "product_name"],
        output_fmt=get_output_format(args),
    )

    if errors:
        return
    print_info(
        "Changing the cluster product initiated. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "CHANGE_COMPUTE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "product_name"],
        output_fmt=get_output_format(args),
    )


def clusters_set_backup_schedule(args: Namespace) -> None:
    body = {
        "backup_hours": args.backup_hours,
    }

    client = Client.from_args(args)
    data, errors = client.put(
        f"/api/v2/clusters/{args.cluster_id}/backup-schedule/", body=body
    )  # type: ignore
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "backup_schedule"],
        output_fmt=get_output_format(args),
    )

    if errors:
        return
    print_info(
        "Changing the cluster backup schedule. "
        "It may take a few minutes to complete the changes."
    )

    _wait_for_completed_operation(
        client=client,
        cluster_id=args.cluster_id,
        request_params={"type": "BACKUP_SCHEDULE_UPDATE", "limit": 1},
    )

    # Re-fetch the cluster's info
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "name", "backup_schedule"],
        output_fmt=get_output_format(args),
    )


def clusters_snapshots_list(args: Namespace) -> None:
    days = args.days_ago
    start = datetime.now(tz=timezone.utc) - timedelta(days=days)
    url = f"/api/v2/clusters/{args.cluster_id}/snapshots/"

    client = Client.from_args(args)
    data, errors = client.get(url, params={"start": start.isoformat()})
    if data is not None and len(data) == 0:
        print_info(
            f"Looks like there are no snapshots for the last {days} days. "
            "Use --days-ago to broaden your search."
        )
        return

    print_response(
        data=data,
        errors=errors,
        keys=[
            "created",
            "repository",
            "snapshot",
        ],
        output_fmt=get_output_format(args),
    )


def clusters_snapshots_restore(args: Namespace) -> None:
    url = f"/api/v2/clusters/{args.cluster_id}/snapshots/restore/"

    body = {
        "repository": args.repository,
        "snapshot": args.snapshot,
    }
    if args.type:
        body["type"] = args.type
    else:
        # fallback for backwards compatibility
        body["type"] = "tables"
    if args.source_cluster_id:
        body["source_cluster_id"] = args.source_cluster_id
    if args.tables:
        tables = args.tables.strip().split(",")
        body["tables"] = [x.strip() for x in tables]
    if args.sections:
        sections = args.sections.strip().split(",")
        body["sections"] = [s.strip() for s in sections]

    client = Client.from_args(args)
    data, errors = client.post(url, body=body)

    if not errors:
        print_info(
            "Restoring the snapshot. Depending on the amount of data you have, this"
            " might take a very long time."
        )

        _wait_for_completed_operation(
            client=client,
            cluster_id=args.cluster_id,
            request_params={"type": "RESTORE_SNAPSHOT", "limit": 1},
        )

    print_response(
        data=data,
        errors=errors,
        keys=[
            "created",
            "repository",
            "snapshot",
        ],
        output_fmt=get_output_format(args),
    )


def export_jobs_create(args: Namespace) -> None:
    body = {
        "source": {
            "table": args.table,
        },
        "destination": {"format": args.file_format},
    }

    if args.compression:
        body["compression"] = args.compression

    client = Client.from_args(args)
    data, errors = client.post(
        f"/api/v2/clusters/{args.cluster_id}/export-jobs/", body=body
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "cluster_id", "status"],
        output_fmt=get_output_format(args),
    )

    if data:
        export_job_id = data["id"]

        _wait_for_completed_operation(
            client=client,
            cluster_id=args.cluster_id,
            request_params={"export_job_id": export_job_id},
            operation_status_func=_get_export_job_operation_status,
            feedback_func=(
                _data_job_feedback_func,
                ("export",),
            ),
            post_success_func=(
                _download_exported_file,
                (client, args.cluster_id, args.save_as, export_job_id),
            ),
        )


def export_jobs_delete(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.delete(
        f"/api/v2/clusters/{args.cluster_id}/export-jobs/{args.export_job_id}/"
    )
    print_response(
        data=data,
        errors=errors,
        keys=["id", "cluster_id", "status"],
        output_fmt=get_output_format(args),
    )


def export_jobs_list(args: Namespace) -> None:
    client = Client.from_args(args)
    data, errors = client.get(f"/api/v2/clusters/{args.cluster_id}/export-jobs/")
    print_response(
        data=data,
        errors=errors,
        keys=["id", "cluster_id", "status", "source", "destination"],
        output_fmt=get_output_format(args),
        transforms={
            "source": _transform_export_job_source,
            "destination": _transform_export_job_destination,
        },
    )


@grand_central_jwt_token
def get_scheduled_jobs(args: Namespace) -> None:
    client = _get_gc_client(args)

    data, errors = client.get("/api/scheduled-jobs/")

    print_response(
        data=data,
        errors=errors,
        keys=["name", "id", "cron", "sql", "enabled", "next_run_time"],
        output_fmt=get_output_format(args),
    )

    if errors or not data:
        return


@grand_central_jwt_token
def get_scheduled_job_log(args: Namespace) -> None:
    client = _get_gc_client(args)

    data, errors = client.get(f"/api/scheduled-jobs/{args.job_id}/log")
    print_response(
        data=data,
        errors=errors,
        keys=["job_id", "start", "end", "error", "statements"],
        output_fmt=get_output_format(args),
    )

    if errors or not data:
        return


@grand_central_jwt_token
def create_scheduled_job(args: Namespace) -> None:
    body = {
        "name": args.name,
        "cron": args.cron,
        "sql": args.sql,
        "enabled": args.enabled,
    }

    client = _get_gc_client(args)

    data, errors = client.post("/api/scheduled-jobs/", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["name", "id", "cron", "sql", "enabled"],
        output_fmt=get_output_format(args),
    )

    if errors or not data:
        return


@grand_central_jwt_token
def delete_scheduled_job(args: Namespace) -> None:
    client = _get_gc_client(args)

    data, errors = client.delete(f"/api/scheduled-jobs/{args.job_id}")
    print_response(
        data=data,
        errors=errors,
        success_message="Scheduled job deleted.",
        output_fmt=get_output_format(args),
    )


@grand_central_jwt_token
def edit_scheduled_job(args: Namespace) -> None:
    body = {
        "name": args.name,
        "cron": args.cron,
        "sql": args.sql,
        "enabled": args.enabled,
    }

    client = _get_gc_client(args)

    data, errors = client.put(f"/api/scheduled-jobs/{args.job_id}", body=body)
    print_response(
        data=data,
        errors=errors,
        keys=["name", "id", "sql", "cron", "enabled"],
        output_fmt=get_output_format(args),
    )

    if errors or not data:
        return


def _get_gc_client(args: Namespace) -> Client:
    client = Client.from_args(args)
    cluster, _ = client.get(f"/api/v2/clusters/{args.cluster_id}/")

    url_region_cloud = cluster.get("fqdn").split(".", 1)[1][:-1]  # type: ignore
    gc_url = f"https://{cluster.get('name')}.gc.{url_region_cloud}"  # type: ignore
    client.base_url = URL(gc_url)
    client.session.cookies.set("grand_central_session", CONFIG.gc_jwt_token)

    return client


def _transform_export_job_source(field):
    return field["table"]


def _transform_export_job_destination(field):
    return f"Format: {field['format']}\nFile ID: {field.get('file', {}).get('id')}"


# We want to map the custom hardware specs to slightly nicer params in croud,
# hence this mapping here
def _handle_edge_params(body, args):
    if args.cpus:
        body.setdefault("hardware_specs", {})["cpus_per_node"] = args.cpus
    if args.disks:
        body.setdefault("hardware_specs", {})["disks_per_node"] = args.disks
    if args.disk_size_gb:
        body.setdefault("hardware_specs", {})["disk_size_per_node_bytes"] = (
            args.disk_size_gb * 1024 * 1024 * 1024
        )
    if args.disk_type:
        body.setdefault("hardware_specs", {})["disk_type"] = args.disk_type
    if args.memory_size_mb:
        body.setdefault("hardware_specs", {})["memory_per_node_bytes"] = (
            args.memory_size_mb * 1024 * 1024
        )


def _get_operation_status(client: Client, cluster_id: str, request_params: Dict):
    data, errors = client.get(
        f"/api/v2/clusters/{cluster_id}/operations/", params=request_params
    )

    if not data or len(data.get("operations", [])) == 0:
        raise AsyncOperationNotFound("Failed retrieving operation status.")

    operation = data["operations"][0]

    status = operation.get("status")
    feedback_data = operation.get("feedback_data", {})
    msg = feedback_data.get("message", None)

    return status, msg, feedback_data


def _get_import_job_operation_status(
    client: Client, cluster_id: str, request_params: Dict
):
    import_job_id = request_params["import_job_id"]
    data, errors = client.get(
        f"/api/v2/clusters/{cluster_id}/import-jobs/{import_job_id}/"
    )

    if not data or not data.get("progress"):
        raise AsyncOperationNotFound("Failed retrieving operation status.")

    status = data["status"]
    feedback_data = {"progress": data["progress"]}
    msg = data["progress"]["message"]

    return status, msg, feedback_data


def _get_formatted_records_normalized(feedback: dict) -> str:
    num_records = feedback.get("progress", {}).get("records")

    records_normalized = num_records

    if num_records > 1_000_000:
        records_normalized = f"{records_normalized / 1_000_000:.2f}M"
    elif num_records > 1_000:
        records_normalized = f"{records_normalized / 1_000:.2f}K"

    return records_normalized


def _data_job_feedback_func(status: str, feedback: dict, job_type: str):
    records_normalized = _get_formatted_records_normalized(feedback)
    percent = feedback.get("progress", {}).get("percent", 0)
    percent_str = ""
    if percent > 0:
        percent_str = "({:.2f}%) ".format(percent)

    if status == "SUCCEEDED":
        print_info(f"Done {job_type}ing {records_normalized} records")
    else:
        print_info(
            f"{job_type}ing... {records_normalized} records {percent_str}{job_type}ed "
            "so far."
        )


def _download_exported_file(
    client: Client, cluster_id: str, save_as: str, export_job_id: str
):
    data, errors = client.get(
        f"/api/v2/clusters/{cluster_id}/export-jobs/{export_job_id}/"
    )

    if not data or not data.get("progress"):
        raise AsyncOperationNotFound("Failed retrieving operation status.")

    status = data["status"]
    if status == "SUCCEEDED":
        file_id = data.get("destination", {}).get("file", {}).get("id")
        if file_id:
            org_id = _get_org_id_from_cluster_id(client, cluster_id)
            data, errors = client.get(
                f"/api/v2/organizations/{org_id}/files/{file_id}/"
            )
            file_data: dict = cast(dict, data)
            if not (file_data and file_data.get("download_url")):
                print_error("File could not be fetched.")
            if not save_as:
                print_success(f"Download URL: {file_data['download_url']}")
                return
            HALO.stop()
            print_info("Downloading file...")

            r = requests.get(
                file_data["download_url"], stream=True, allow_redirects=True
            )
            if r.status_code != 200:
                r.raise_for_status()
                print_error(
                    f"Request to {file_data['download_url']} returned status code "
                    f"{r.status_code}"
                )
            file_size = int(r.headers.get("Content-Length", 0))

            path = pathlib.Path(save_as).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)

            desc = "(Unknown total file size)" if file_size == 0 else ""
            r.raw.read = functools.partial(r.raw.read, decode_content=True)
            with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
                with path.open("wb") as f:
                    copyfileobj(r_raw, f)

            print_success(f"Successfully downloaded file to {path}")


def _get_export_job_operation_status(
    client: Client, cluster_id: str, request_params: Dict
):
    export_job_id = request_params["export_job_id"]
    data, errors = client.get(
        f"/api/v2/clusters/{cluster_id}/export-jobs/{export_job_id}/"
    )

    if not data or not data.get("progress"):
        raise AsyncOperationNotFound("Failed retrieving export operation status.")

    status = data["status"]
    feedback_data = {"progress": data["progress"]}
    msg = data["progress"]["message"]

    return status, msg, feedback_data


def _wait_for_completed_operation(
    *,
    client: Client,
    cluster_id: str,
    request_params: Dict,
    operation_status_func=_get_operation_status,
    feedback_func=None,
    post_success_func=None,
):
    last_status = None
    last_msg = None
    while True:
        try:
            status, msg, feedback = operation_status_func(
                client=client, cluster_id=cluster_id, request_params=request_params
            )
        except AsyncOperationNotFound as e:
            print_error(str(e))
            break

        # Inform about a change in status if the status is not final.
        if status not in ["FAILED", "SUCCEEDED"] and (
            last_status != status or msg != last_msg
        ):
            to_print = f"Status: {status} ({msg})" if msg else f"Status: {status}"
            print_info(to_print)
            last_status = status
            last_msg = msg

        # Call for custom feedback if function available and there is status to report.
        if status in ["IN_PROGRESS", "SUCCEEDED"] and feedback_func:
            (feedback_f, feedback_args) = feedback_func
            feedback_f(status, feedback, *feedback_args)

        # Final statuses
        if status == "SUCCEEDED":
            if post_success_func:
                (func, call_args) = post_success_func
                func(*call_args)
            print_success("Operation completed.")
            break
        if status == "FAILED":
            if msg:
                print_error(msg)
            else:
                print_error(
                    "Your cluster operation has failed. "
                    "Our operations team is investigating the issue."
                )
            break

        with HALO:
            time.sleep(10)


def _lookup_organization_id_for_project(
    client: Client, args: Namespace, project_id: str
) -> Optional[str]:
    data, errors = client.get(f"/api/v2/projects/{project_id}/")
    if not data or errors:
        print_response(
            data=data,
            errors=errors,
            output_fmt=get_output_format(args),
        )
        return None
    return data.get("organization_id")
