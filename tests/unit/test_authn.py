"""
Tests for the callback endpoint (where users are sent by UAA after logging in)
"""
import json
from urllib import parse
import datetime
import random
import requests_mock
import string

def make_random_token():
    return "".join(random.choice(string.ascii_letters) for i in range(10))

def check_token_body(request):
    # this is for requests_mock
    data = request.text
    data = parse.parse_qs(data)
    assert data["grant_type"][0] == "authorization_code"
    assert data["code"][0] == "1234"
    assert data["redirect_uri"][0] == "http://localhost/cb"
    return True


def test_callback_happy_path(client, fake_jwt_token, simple_org_response, simple_space_response, uaa_user_groups_response):
    # go to a page to get redirected to log in
    response = client.get("/foo")
    location_str = f"{response.headers['location']}"
    location = parse.urlparse(location_str)
    query_params = parse.parse_qs(location.query)
    csrf = query_params["state"][0]
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_random_token(),
            "refresh_token": make_random_token(),
            "token_type": "bearer",
            "id_token": fake_jwt_token,
            "expires_in": 2000,
            "scope": "openid cloud_controller.read scim.read",
            "jti": "idk",
        }
        m.post(
            "mock://uaa/token",
            additional_matcher=check_token_body,
            text=json.dumps(body),
        )
        m.get(
            "mock://uaa/users?attributes=groups&filter=id eq 'test_user'",
            text=uaa_user_groups_response,
        )
        m.get(
            "mock://cf/v3/roles?user_guids=test_user&types=space_developer,space_manager,space_auditor",
            text=simple_space_response,
        )
        m.get(
            "mock://cf/v3/roles?user_guids=test_user&types=organization_manager,organization_auditor",
            text=simple_org_response,
        )
        resp = client.get(f"/cb?code=1234&state={csrf}")
        assert m.called
    with client.session_transaction() as s:
        # nuke the CSRF token
        assert s.get("state") is None
        # make sure we're logged in
        assert s.get("user_id") is not None
        assert s.get("access_token") is not None
        assert s.get("refresh_token") is not None
        assert s.get("access_token_expiration") is not None
        assert s.get("id_token") is not None
        assert s.get("spaces") == ["space-guid-1"]
        assert s.get("orgs") == ["org-guid-1"]
        # assert sorted(s.get("groups")) == sorted(["cloud_controller.admin", "network.admin"])
    assert resp.status_code == 302
    assert resp.headers.get("location").endswith("/foo")


def test_callback_bad_csrf(client, fake_jwt_token):
    # go to a page to get redirected to log in
    client.get("/foo")
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_random_token(),
            "token_type": "bearer",
            "id_token": fake_jwt_token,
            "expires_in": 2000,
            "scope": "openid email",
            "jti": "idk",
        }
        m.post(
            "mock://uaa/token",
            additional_matcher=check_token_body,
            text=json.dumps(body),
        )
        resp = client.get(f"/cb?code=1234&state=badcsrf")
        assert not m.called
    with client.session_transaction() as s:
        # nuke the CSRF token
        assert s.get("state") is None
        # make sure we're not logged in
        assert s.get("user_id") is None
    assert resp.status_code == 403


def test_callback_no_csrf(client, fake_jwt_token):
    # go to a page to get redirected to log in
    client.get("/foo")
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_random_token(),
            "token_type": "bearer",
            "id_token": fake_jwt_token,
            "expires_in": 2000,
            "scope": "openid cloud_controller.read scim.read",
            "jti": "idk",
        }
        m.post(
            "mock://uaa/token",
            additional_matcher=check_token_body,
            text=json.dumps(body),
        )
        resp = client.get(f"/cb?code=1234")
        assert not m.called
    with client.session_transaction() as s:
        # nuke the CSRF token
        assert s.get("state") is None
        # make sure we're logged in
        assert s.get("user_id") is None
    assert resp.status_code == 403


def test_uaa_token_refreshed(client):
    # check that a user with a token expiring soon has their token refreshed
    refresh_token = make_random_token()
    token_expiration = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(seconds=1)

    def validate_request(request):
        data = request.text
        data = parse.parse_qs(data)
        assert data["grant_type"][0] == "refresh_token"
        assert data["refresh_token"][0] == refresh_token
        return True

    with client.session_transaction() as s:
        # set up user session
        s["user_id"] = "1234"
        s["access_token"] = make_random_token()
        s["refresh_token"] = refresh_token
        s["access_token_expiration"] = token_expiration.timestamp()

    new_access_token = make_random_token()
    new_refresh_token = make_random_token()

    with requests_mock.Mocker() as m:
        body = {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 2000,
        }
        m.post(
            "mock://uaa/token",
            additional_matcher=validate_request,
            text=json.dumps(body),
        )
        client.get("/ping")
        assert m.called

    with client.session_transaction() as s:
        assert s["access_token"] == new_access_token
        assert s["refresh_token"] == new_refresh_token
