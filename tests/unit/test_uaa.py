import requests_mock
from kibana_cf_auth_proxy import uaa


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
