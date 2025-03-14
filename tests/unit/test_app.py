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
    assert location.scheme == "http"
    assert location.hostname == "mock.uaa"
    assert query_params["redirect_uri"][0][0:4] == "http"
    assert query_params["scope"][0] == "openid cloud_controller.read scim.read"
    assert query_params["response_type"][0] == "code"


def test_app_proxies_arbitrary_paths(authenticated_client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/foo/bar/baz/quux/")
        authenticated_client.get("/foo/bar/baz/quux/")
    assert m.called


def test_app_filters_headers(authenticated_client):
    """
    if we send one of the permission-related headers with our own value
    it should be dropped or changed
    """
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/foo/bar/baz/quux/")
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
            "http://mock.dashboard/home",
            request_headers={"x-proxy-ext-orgids": r'"org-id-1", "org-id-2"'},
        )
        with client.session_transaction() as s:
            s["user_id"] = "me2"  # set user id so we don't get authed
            s["email"] = "me"
            s["orgs"] = ["org-id-1", "org-id-2"]
        client.get("/home")


def test_spaces_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get(
            "http://mock.dashboard/home",
            request_headers={"x-proxy-ext-spaceids": r'"space-id-1", "space-id-2"'},
        )
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
            s["spaces"] = ["space-id-1", "space-id-2"]
        client.get("/home")


def test_admin_role_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/home")
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
            s["groups"] = ["admin"]
            s["is_cf_admin"] = True
        client.get("/home")
        assert "admin" in m.last_request._request.headers["x-proxy-roles"]


def test_user_org_roles_set_correctly(client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/home")
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
            s["user_orgs"] = ["org-1", "org-2"]
        client.get("/home")
        assert m.last_request._request.headers["x-proxy-roles"] == "org-1,org-2"


def test_adds_xff_when_it_is_not_set(client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/home")
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
        client.get("/home")
        assert m.last_request._request.headers["X-Forwarded-For"]


def test_does_not_modify_existing_xff_uppercase(client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/home")
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
        client.get("/home", headers={"X-Forwarded-For": "x.x.x.x"})
        assert m.last_request._request.headers["X-Forwarded-For"] == "x.x.x.x"


def test_does_not_modify_existing_xff_lowercase(client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/home")
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
        client.get("/home", headers={"x-forwarded-for": "y.y.y.y"})
        assert m.last_request._request.headers["X-Forwarded-For"] == "y.y.y.y"


def test_does_not_accept_truthy_is_cf_admin(client):
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/home")
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["is_cf_admin"] = "truthy"
            s["email"] = "me"
        client.get("/home")
        assert "admin" not in m.last_request._request.headers["x-proxy-roles"]


def test_callback_returns_error_on_uaa_token_failure(client):
    with requests_mock.Mocker() as m:
        m.post("http://mock.uaa/token", status_code=401)
        with client.session_transaction() as s:
            s["user_id"] = "me2"
            s["email"] = "me"
            s["state"] = "foo"
        response = client.get("/cb?code=fakecode&state=foo")
        assert response.status_code == 500
