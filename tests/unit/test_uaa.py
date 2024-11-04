import pytest
import requests_mock
from cf_auth_proxy import uaa


def test_user_is_admin(uaa_user_is_admin_response):
    with requests_mock.Mocker() as m:
        m.get(
            "http://mock.uaa/Users/a-user-id",
            text=uaa_user_is_admin_response,
        )
        isAdmin = uaa.is_user_cf_admin("a-user-id", "a-token")
        assert isAdmin
        assert m.last_request._request.headers["Authorization"] == "Bearer a-token"


def test_user_is_not_admin(uaa_user_is_not_admin_response):
    with requests_mock.Mocker() as m:
        m.get(
            "http://mock.uaa/Users/a-user-id",
            text=uaa_user_is_not_admin_response,
        )
        isAdmin = uaa.is_user_cf_admin("a-user-id", "a-token")
        assert not isAdmin
        assert m.last_request._request.headers["Authorization"] == "Bearer a-token"


def test_user_has_no_groups(uaa_user_has_no_groups_response):
    with requests_mock.Mocker() as m:
        m.get(
            "http://mock.uaa/Users/a-user-id",
            text=uaa_user_has_no_groups_response,
        )
        isAdmin = uaa.is_user_cf_admin("a-user-id", "a-token")
        assert not isAdmin
        assert m.last_request._request.headers["Authorization"] == "Bearer a-token"


def test_uaa_has_unexpected_error():
    with requests_mock.Mocker() as m:
        m.get("http://mock.uaa/Users/a-user-id", status_code=500)
        with pytest.raises(Exception):
            uaa.is_user_cf_admin("a-user-id", "a-token")


def test_uaa_has_unauthorized_error():
    with requests_mock.Mocker() as m:
        m.get("http://mock.uaa/Users/a-user-id", status_code=401)
        with pytest.raises(Exception):
            uaa.is_user_cf_admin("a-user-id", "a-token")


def test_uaa_get_client_credentials_token_raises_unexpected_error():
    with requests_mock.Mocker() as m:
        m.post("http://mock.uaa/token", status_code=500)
        with pytest.raises(Exception):
            uaa.get_client_credentials_token()
