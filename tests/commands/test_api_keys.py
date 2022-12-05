from unittest import mock
import pytest
from croud.api import Client, RequestMethod
from tests.util import call_command, assert_rest


@mock.patch.object(Client, "request", return_value=({}, None))
def test_api_keys_list(mock_request):

    call_command("croud", "api-keys", "list")
    assert_rest(
        mock_request,
        RequestMethod.GET,
        f"/api/v2/users/me/api-keys/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_api_keys_create(mock_request):

    call_command("croud", "api-keys", "create")
    assert_rest(
        mock_request,
        RequestMethod.POST,
        f"/api/v2/users/me/api-keys/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_api_keys_delete(mock_request):

    call_command("croud", "api-keys", "delete", "--api-key", "key-to-be-deleted")
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        f"/api/v2/users/me/api-keys/key-to-be-deleted/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@pytest.mark.parametrize("target_status", [True, False])
def test_api_keys_edit(mock_request, target_status):
    target_status = True
    if target_status:
        target_status_str = "true"
    else:
        target_status_str = "false"

    call_command("croud", "api-keys", "edit", "--api-key", "target-key", "--active", target_status_str)
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        f"/api/v2/users/me/api-keys/target-key/",
        body={"active": target_status},
    )