from unittest import mock

from croud.api import Client, RequestMethod
from tests.util import assert_rest, call_command, gen_uuid


@mock.patch.object(Client, "request", return_value=({}, None))
def test_cloud_configurations_get_org_override(mock_request):
    org_id = gen_uuid()
    call_command(
        "croud",
        "cloud-configurations",
        "get",
        "--key",
        "my_config_key",
        "--org-id",
        org_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/configurations/my_config_key/",
        params={"organization_id": org_id},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_cloud_configurations_set_org_override(mock_request):
    org_id = gen_uuid()
    call_command(
        "croud",
        "cloud-configurations",
        "set",
        "--key",
        "my_config_key",
        "--value",
        "new_config_value",
        "--org-id",
        org_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        "/api/v2/configurations/my_config_key/",
        body={"value": "new_config_value", "organization_id": org_id},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_cloud_configurations_list_org_override(mock_request):
    org_id = gen_uuid()
    call_command("croud", "cloud-configurations", "list", "--org-id", org_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/configurations/",
        params={"organization_id": org_id},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_cloud_configurations_get_user_override(mock_request):
    user_id = gen_uuid()
    call_command(
        "croud",
        "cloud-configurations",
        "get",
        "--key",
        "my_config_key",
        "--user-id",
        user_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/configurations/my_config_key/",
        params={"user_id": user_id},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_cloud_configurations_set_user_override(mock_request):
    user_id = gen_uuid()
    call_command(
        "croud",
        "cloud-configurations",
        "set",
        "--key",
        "my_config_key",
        "--value",
        "new_config_value",
        "--user-id",
        user_id,
    )
    assert_rest(
        mock_request,
        RequestMethod.PUT,
        "/api/v2/configurations/my_config_key/",
        body={"value": "new_config_value", "user_id": user_id},
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_cloud_configurations_list_user_override(mock_request):
    user_id = gen_uuid()
    call_command("croud", "cloud-configurations", "list", "--user-id", user_id)
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/configurations/",
        params={"user_id": user_id},
    )
