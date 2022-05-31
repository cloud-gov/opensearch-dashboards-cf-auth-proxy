import json
import requests_mock

from kibana_cf_auth_proxy import uaa

def test_gets_client_credentials_token(fake_jwt_token, uaa_user_groups_response):
    with requests_mock.Mocker() as m:
        body = {
            "access_token": fake_jwt_token,
            "token_type": "bearer",
            "expires_in": 2000,
            "scope": "scim.read",
            "jti": "idk",
        }
        m.post(
            "mock://uaa/token",
            # additional_matcher=check_token_body,
            text=json.dumps(body),
        )
        m.get(
            "mock://uaa/Users?attributes=groups&filter=id eq 'a-user-id'",
            text=uaa_user_groups_response,
        )
        uaa.get_user_groups("a-user-id")
        # assert sorted(uaa.get_user_groups("a-user-id")) == sorted(
        #     ["cloud_controller.admin", "network.admin"]
        # )

def test_gets_user_groups(uaa_user_groups_response):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://uaa/Users?attributes=groups&filter=id eq 'a-user-id'",
            text=uaa_user_groups_response,
        )
        assert sorted(uaa.get_user_groups("a-user-id", "a_token")) == sorted(
            ["cloud_controller.admin", "network.admin"]
        )