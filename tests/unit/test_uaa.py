import json
import requests_mock

from kibana_cf_auth_proxy import uaa

def test_gets_user_groups(uaa_user_groups_response):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://uaa/Users?attributes=groups&filter=id eq 'a-user-id'",
            text=uaa_user_groups_response,
        )
        assert sorted(uaa.get_user_groups("a-user-id", "a_token")) == sorted(
            ["cloud_controller.admin", "network.admin"]
        )