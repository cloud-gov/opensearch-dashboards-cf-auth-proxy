import requests_mock
from kibana_cf_auth_proxy import uaa


def test_user_is_admin(uaa_user_is_admin_response):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://uaa/Users?attributes=groups&filter=id eq 'a-user-id'",
            text=uaa_user_is_admin_response,
        )
        assert uaa.is_user_cf_admin("a-user-id", "a-token") is True


def test_user_is_not_admin(uaa_user_is_not_admin_response):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://uaa/Users?attributes=groups&filter=id eq 'a-user-id'",
            text=uaa_user_is_not_admin_response,
        )
        assert not uaa.is_user_cf_admin("a-user-id", "a-token")
