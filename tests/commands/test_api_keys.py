from unittest import mock

import pytest

from croud.api import Client, RequestMethod
from tests.util import assert_rest, call_command


@mock.patch.object(Client, "request", return_value=({}, None))
def test_api_keys_list(mock_request):
    call_command("croud", "api-keys", "list")
    assert_rest(
        mock_request,
        RequestMethod.GET,
        "/api/v2/users/me/api-keys/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_api_keys_create(mock_request):
    call_command("croud", "api-keys", "create")
    assert_rest(
        mock_request,
        RequestMethod.POST,
        "/api/v2/users/me/api-keys/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
def test_api_keys_delete(mock_request):
    call_command("croud", "api-keys", "delete", "--api-key", "key-to-be-deleted")
    assert_rest(
        mock_request,
        RequestMethod.DELETE,
        "/api/v2/users/me/api-keys/key-to-be-deleted/",
        params=None,
    )


@mock.patch.object(Client, "request", return_value=({}, None))
@pytest.mark.parametrize("target_status", [True, False])
def test_api_keys_edit(mock_request, target_status):
    call_command(
        "croud",
        "api-keys",
        "edit",
        "--api-key",
        "target-key",
        "--active",
        str(target_status).lower(),
    )
    assert_rest(
        mock_request,
        RequestMethod.PATCH,
        "/api/v2/users/me/api-keys/target-key/",
        body={"active": target_status},
    )
