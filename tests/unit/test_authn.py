"""
Tests for the callback endpoint (where users are sent by UAA after logging in)
"""
import json
import jwt
import datetime
import random
import requests_mock
import string

from urllib import parse

from cf_auth_proxy.extensions import config


def make_jwt_token(claims=None):
    # todo, clean this up
    claims = claims or {"user_id": "test_user"}
    token = jwt.encode(claims, "", "HS256")
    return token


def make_random_token():
    return "".join(random.choice(string.ascii_letters) for i in range(10))


def is_auth_code_token_request(request):
    return "grant_type=authorization_code" in request.text


def is_valid_auth_code_token_request(request):
    data = request.text
    data = parse.parse_qs(data)
    assert data["grant_type"][0] == "authorization_code"
    assert data["code"][0] == "1234"
    assert data["redirect_uri"][0] == "http://localhost/cb"


def is_client_credentials_token_request(request):
    return "grant_type=client_credentials" in request.text


def test_callback_happy_path(
    client,
    simple_org_response,
    simple_space_response,
    uaa_user_is_admin_response,
):
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
            "id_token": make_jwt_token(),
            "expires_in": 2000,
            "scope": "openid cloud_controller.read scim.read",
            "jti": "idk",
        }
        m.post(
            "http://mock.uaa/token",
            additional_matcher=is_auth_code_token_request,
            text=json.dumps(body),
        )
        client_creds_response = {
            "access_token": make_jwt_token(),
            "token_type": "bearer",
            "expires_in": 2000,
            "scope": "scim.read",
            "jti": "idk",
        }
        m.post(
            "http://mock.uaa/token",
            additional_matcher=is_client_credentials_token_request,
            text=json.dumps(client_creds_response),
        )
        m.get(
            "http://mock.uaa/Users/test_user",
            text=uaa_user_is_admin_response,
        )
        m.get(
            "http://mock.cf/v3/roles?user_guids=test_user&types=space_developer,space_manager,space_auditor",
            text=simple_space_response,
        )
        m.get(
            "http://mock.cf/v3/roles?user_guids=test_user&types=organization_manager,organization_auditor",
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
        assert s.get("client_credentials_token") is not None
        assert s.get("is_cf_admin") is True

    is_valid_auth_code_token_request(m.request_history[0])

    client_creds_token_request = m.request_history[3]
    data = client_creds_token_request.text
    data = parse.parse_qs(data)
    assert data["grant_type"][0] == "client_credentials"
    assert data["response_type"][0] == "token"
    assert data["client_id"][0] == config.UAA_CLIENT_ID
    assert data["client_secret"][0] == config.UAA_CLIENT_SECRET

    assert resp.status_code == 302
    assert resp.headers.get("location").endswith("/foo")


def test_callback_bad_csrf(client):
    # go to a page to get redirected to log in
    client.get("/foo")
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_random_token(),
            "token_type": "bearer",
            "id_token": make_jwt_token(),
            "expires_in": 2000,
            "scope": "openid email",
            "jti": "idk",
        }
        m.post(
            "http://mock.uaa/token",
            additional_matcher=is_auth_code_token_request,
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


def test_callback_no_csrf(client):
    # go to a page to get redirected to log in
    client.get("/foo")
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_random_token(),
            "token_type": "bearer",
            "id_token": make_jwt_token(),
            "expires_in": 2000,
            "scope": "openid cloud_controller.read scim.read",
            "jti": "idk",
        }
        m.post(
            "http://mock.uaa/token",
            additional_matcher=is_auth_code_token_request,
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
            "http://mock.uaa/token",
            additional_matcher=validate_request,
            text=json.dumps(body),
        )
        client.get("/ping")
        assert m.called

    with client.session_transaction() as s:
        assert s["access_token"] == new_access_token
        assert s["refresh_token"] == new_refresh_token
