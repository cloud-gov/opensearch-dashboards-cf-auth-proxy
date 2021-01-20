import requests_mock

def test_app_pongs(client):
    resp = client.get("/ping")
    assert resp.data == b"PONG"


def test_app_proxies_arbitrary_paths(client):
    """
    This test will break once we start adding auth and stuff
    """
    with requests_mock.Mocker() as m:
        m.get("mock://kibana/foo/bar/baz/quux/")
        client.get("/foo/bar/baz/quux/")
    assert m.called


def test_app_filters_headers(client):
    """
    This test will break once we start adding auth and stuff
    """
    with requests_mock.Mocker() as m:
        m.get("mock://kibana/foo/bar/baz/quux/")
        client.get("/foo/bar/baz/quux/", headers={"X-pRoXy-UsEr": "administrator"})
        for header in m.request_history[0]._request.headers:
            assert header.lower() != "x-proxy-user"
