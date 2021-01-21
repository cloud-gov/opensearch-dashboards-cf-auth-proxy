from urllib import parse
import pytest
import requests_mock


def test_app_pongs(client):
    resp = client.get("/ping")
    assert resp.data == b"PONG"


def test_redirected_to_auth(client):
    response = client.get("/foo")
    location_str = f"{response.headers['location']}"
    location = parse.urlparse(location_str)
    query_params = parse.parse_qs(location.query)
    assert response.status_code == 302
    assert query_params["state"] is not None
    assert location.scheme == "mock"
    assert query_params["redirect_uri"][0][0:4] == "http"
    assert query_params["scope"][0] == "openid email"
    assert query_params["response_type"][0] == "code"


def test_callback(client):
    response = client.get("/foo")


def test_app_proxies_arbitrary_paths(authenticated_client):
    with requests_mock.Mocker() as m:
        m.get("mock://kibana/foo/bar/baz/quux/")
        authenticated_client.get("/foo/bar/baz/quux/")
    assert m.called


def test_app_filters_headers(authenticated_client):
    with requests_mock.Mocker() as m:
        m.get("mock://kibana/foo/bar/baz/quux/")
        authenticated_client.get("/foo/bar/baz/quux/", headers={"X-pRoXy-UsEr": "administrator"})
        for header in m.request_history[0]._request.headers:
            assert header.lower() != "x-proxy-user"
