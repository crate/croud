from unittest import mock

from croud.api import Client, RequestMethod
from tests.util import assert_rest, call_command, gen_uuid


@mock.patch.object(Client, "request", return_value=({}, None))
def test_create_job(mock_request):
    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.POST:
            return {
                "name": "test-job",
                "id": gen_uuid(),
                "cron": "1 1 * * *",
                "sql": "CREATE TABLE test (id TEXT)",
                "enable": True,
            }, None
        if args[0] == RequestMethod.GET and "/jwt/" in args[1]:
            return {
                "token": "xyz",
                "expiry": "01.02.2024",
            }, None
        if args[0] == RequestMethod.GET:
            return {"fqdn": "my.cluster.cloud", "name": "mycluster"}, None
        return None, None

    mock_request.side_effect = mock_call

    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "scheduled-jobs",
        "create",
        "--name",
        "test-job",
        "--cluster-id",
        cluster_id,
        "--cron",
        "1 1 * * *",
        "--sql",
        "CREATE TABLE test (id TEXT)",
        "--enabled",
        "True",
    )

    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/jwt/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/scheduled-jobs/",
        body={
            "name": "test-job",
            "cron": "1 1 * * *",
            "sql": "CREATE TABLE test (id TEXT)",
            "enabled": "True",
        },
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_get_scheduled_jobs(mock_request):
    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/jwt/" in args[1]:
            return {
                "token": "xyz",
                "expiry": "01.02.2024",
            }, None
        if args[0] == RequestMethod.GET:
            return {"fqdn": "my.cluster.cloud", "name": "mycluster"}, None
        if args[0] == RequestMethod.GET and "/scheduled-jobs/" in args[1]:
            return {
                "name": "test-job",
                "id": gen_uuid(),
                "cron": "1 1 * * *",
                "sql": "CREATE TABLE test (id TEXT)",
                "enabled": True,
                "next_run_time": "02.02.2024",
            }, None
        return None, None

    mock_request.side_effect = mock_call

    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "scheduled-jobs",
        "list",
        "--cluster-id",
        cluster_id,
    )

    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/jwt/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/scheduled-jobs/",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_get_scheduled_job_log(mock_request):
    job_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/jwt/" in args[1]:
            return {
                "token": "xyz",
                "expiry": "01.02.2024",
            }, None
        if args[0] == RequestMethod.GET:
            return {"fqdn": "my.cluster.cloud", "name": "mycluster"}, None
        if args[0] == RequestMethod.GET and "/scheduled-jobs/" in args[1]:
            return {
                "job_id": job_id,
                "start": "02.02.2024",
                "end": "03.02.2024",
                "error": None,
                "statements": "CREATE TABLE test (id TEXT)",
            }, None
        return None, None

    mock_request.side_effect = mock_call

    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "scheduled-jobs",
        "logs",
        "--job-id",
        job_id,
        "--cluster-id",
        cluster_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/jwt/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/scheduled-jobs/{job_id}/log",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_delete_scheduled_job(mock_request):
    job_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/jwt/" in args[1]:
            return {
                "token": "xyz",
                "expiry": "01.02.2024",
            }, None
        if args[0] == RequestMethod.GET:
            return {"fqdn": "my.cluster.cloud", "name": "mycluster"}, None
        return None, None

    mock_request.side_effect = mock_call

    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "scheduled-jobs",
        "delete",
        "--job-id",
        job_id,
        "--cluster-id",
        cluster_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/jwt/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/scheduled-jobs/{job_id}",
        any_times=True,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_edit_scheduled_job(mock_request):
    job_id = gen_uuid()

    def mock_call(*args, **kwargs):
        if args[0] == RequestMethod.GET and "/jwt/" in args[1]:
            return {
                "token": "xyz",
                "expiry": "01.02.2024",
            }, None
        if args[0] == RequestMethod.GET:
            return {"fqdn": "my.cluster.cloud", "name": "mycluster"}, None
        if args[0] == RequestMethod.PUT:
            return {
                "name": "test-job-edit",
                "id": gen_uuid(),
                "cron": "2 2 * * *",
                "sql": "CREATE TABLE test (id TEXT)",
                "enabled": False,
                "next_run_time": "02.02.2024",
            }, None
        return None, None

    mock_request.side_effect = mock_call

    cluster_id = gen_uuid()
    call_command(
        "croud",
        "clusters",
        "scheduled-jobs",
        "edit",
        "--job-id",
        job_id,
        "--cluster-id",
        cluster_id,
        "--name",
        "test-job-edit",
        "--cron",
        "2 2 * * *",
        "--sql",
        "CREATE TABLE test (id TEXT)",
        "--enabled",
        "False",
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/jwt/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/clusters/{cluster_id}/",
        any_times=True,
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        f"/api/scheduled-jobs/{job_id}",
        body={
            "name": "test-job-edit",
            "cron": "2 2 * * *",
            "sql": "CREATE TABLE test (id TEXT)",
            "enabled": "False",
        },
        any_times=True,
    )
