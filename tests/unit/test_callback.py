"""
Tests for the callback endpoint (where users are sent by UAA after logging in)
"""
import json
from urllib import parse

import jwt
import pytest
import requests_mock


def check_token_body(request):
    # this is for requests_mock
    data = request.text
    data = parse.parse_qs(data)
    assert data["grant_type"][0] == "authorization_code"
    assert data["code"][0] == "1234"
    assert data["redirect_uri"][0] == "http://localhost/cb"
    return True


def make_id_token(claims=None):
    # todo, clean this up
    claims = claims or {"user_id": "test_user"}
    token = jwt.encode(claims, "", "HS256")
    return token


def make_access_token(claims=None):
    claims = claims or {"user_id": "test_user"}
    token = jwt.encode(claims, "", "HS256")
    return token


def test_callback_happy_path(client):
    # go to a page to get redirected to log in
    response = client.get("/foo")
    location_str = f"{response.headers['location']}"
    location = parse.urlparse(location_str)
    query_params = parse.parse_qs(location.query)
    csrf = query_params["state"][0]
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_access_token(),
            "token_type": "bearer",
            "id_token": make_id_token(),
            "expires_in": 2000,
            "scope": "openid email",
            "jti": "idk",
        }
        m.post(
            "mock://uaa/token",
            additional_matcher=check_token_body,
            text=json.dumps(body),
        )
        client.get(f"/cb?code=1234&state={csrf}")
        assert m.called
    with client.session_transaction() as s:
        # nuke the CSRF token
        assert s.get("state") is None
        # make sure we're logged in
        assert s.get("user_id") is not None


def test_callback_bad_csrf(client):
    # go to a page to get redirected to log in
    response = client.get("/foo")
    location_str = f"{response.headers['location']}"
    location = parse.urlparse(location_str)
    query_params = parse.parse_qs(location.query)
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_access_token(),
            "token_type": "bearer",
            "id_token": make_id_token(),
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
        # make sure we're logged in
        assert s.get("user_id") is None
    assert resp.status_code == 403


def test_callback_no_csrf(client):
    # go to a page to get redirected to log in
    response = client.get("/foo")
    location_str = f"{response.headers['location']}"
    location = parse.urlparse(location_str)
    query_params = parse.parse_qs(location.query)
    with requests_mock.Mocker() as m:
        body = {
            "access_token": make_access_token(),
            "token_type": "bearer",
            "id_token": make_id_token(),
            "expires_in": 2000,
            "scope": "openid email",
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
