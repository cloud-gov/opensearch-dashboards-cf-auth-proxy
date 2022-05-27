import requests_mock

from kibana_cf_auth_proxy import uaa

def test_gets_groups(simple_users_response):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://uaa/Users?attributes=groups&filter=id eq 'a-user-id'",
            text=simple_users_response,
        )
        assert sorted(uaa.get_user_groups("a-user-id", "a_token")) == sorted(
            ["cloud_controller.admin"]
        )