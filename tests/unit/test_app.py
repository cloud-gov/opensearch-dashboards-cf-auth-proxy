import pickle
import time

from urllib import parse
import pytest
import requests_mock
import flask


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
    assert query_params["scope"][0] == "openid cloud_controller.read scim.read"
    assert query_params["response_type"][0] == "code"


def test_app_proxies_arbitrary_paths(authenticated_client):
    with requests_mock.Mocker() as m:
        m.get("mock://kibana/foo/bar/baz/quux/")
        authenticated_client.get("/foo/bar/baz/quux/")
    assert m.called


def test_app_filters_headers(authenticated_client):
    """
    if we send one of the permission-related headers with our own value
    it should be dropped or changed
    """
    with requests_mock.Mocker() as m:
        m.get("mock://kibana/foo/bar/baz/quux/")
        authenticated_client.get(
            "/foo/bar/baz/quux/",
            headers={
                "X-pRoXy-UsEr": "administrator",
                "x-proxy-roles": "batman",
                "x-proxy-ext-spaceids": "1,2,3",
                "x-proxy-ext-orgids": "4,5,6",
            },
        )
        for header in m.request_history[0]._request.headers:
            if header.lower() == "x-proxy-user":
                assert m.request_history[0]._request.headers[header] != "administrator"
            if header.lower() == "x-proxy-roles":
                assert m.request_history[0]._request.headers[header] != "batman"
            if header.lower() == "x-proxy-ext-spaceids":
                assert m.request_history[0]._request.headers[header] != "1,2,3"
            if header.lower() == "x-proxy-ext-orgids":
                assert m.request_history[0]._request.headers[header] != "4,5,6"


def test_session_refreshes(client):
    """
    So this test ended up not really being needed, but I'm leaving it in because it's
    testing an interface that I don't really trust that much.

    This test validates that the user's session gets updated every time the user
    hits a page. The default SessionInterface, SecureCookieSessionInterface no-ops on
    save_session when the session is not modified. flask-session's SessionInterfaces
    (FileSystemCacheSessionInterface and RedisSessionInteface) both save the session
    on every request, with the updated session timeout, so we don't need to refresh
    the session. Since this is different from all the session documentation on Flask,
    it seems very possible the library will change in the future to match the default
    behavior more closely, so this test will tell us we need to do something when that 
    happens.
    """
    client.get("/ping")
    session_interface = flask.current_app.session_interface
    cache = session_interface.cache
    session_id = client.cookie_jar._cookies["localhost.local"]["/"]["cfsession"].value
    session_backing = session_interface.key_prefix + session_id
    filename = cache._get_filename(session_backing)
    with open(filename, "rb") as f:
        timestamp = pickle.load(f)
    time.sleep(1)
    client.get("/ping")
    with open(filename, "rb") as f:
        timestamp_after = pickle.load(f)
    assert timestamp < timestamp_after


def test_orgs_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://kibana/home",
            request_headers={"x-proxy-ext-orgids": r'"org-id-1", "org-id-2"'},
        )
        with client.session_transaction() as s:
            s["user_id"] = "me"  # set user id so we don't get authed
            s["orgs"] = ["org-id-1", "org-id-2"]
        client.get("/home")


def test_spaces_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://kibana/home",
            request_headers={"x-proxy-ext-spaceids": r'"space-id-1", "space-id-2"'},
        )
        with client.session_transaction() as s:
            s["user_id"] = "me"
            s["spaces"] = ["space-id-1", "space-id-2"]
        client.get("/home")
