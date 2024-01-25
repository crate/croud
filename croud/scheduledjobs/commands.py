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

from yarl import URL

from croud.api import Client
from croud.config import CONFIG, get_output_format
from croud.printer import print_response
from croud.util import grand_central_jwt_token


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
    client.session.cookies.set("cratedb_center_session", CONFIG.gc_jwt_token)

    return client
