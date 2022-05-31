from urllib import parse
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

def test_user_role_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://kibana/home",
            request_headers={"x-proxy-roles": r'"user"'},
        )
        with client.session_transaction() as s:
            s["user_id"] = "me"
        client.get("/home")

def test_admin_role_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get(
            "mock://kibana/home",
            request_headers={"x-proxy-roles": r'"admin"'},
        )
        with client.session_transaction() as s:
            s["user_id"] = "me"
            s["groups"] = ["admin"]
            s["is_cf_admin"] = True
        client.get("/home")
