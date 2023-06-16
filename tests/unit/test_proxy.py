import pytest
import requests_mock
from kibana_cf_auth_proxy import proxy


def test_proxy_returns_200():
    with requests_mock.Mocker() as m:
        m.get("http://mock.dashboard/world", text="hello")
        response = proxy.proxy_request(
            "http://mock.dashboard/world",
            {"user-agent": "special-user-agent"},
            None,
            {},
            "GET",
        )
    assert response.data.decode("utf-8") == "hello"
    assert (
        m.request_history[0]._request.headers.get("User-Agent") == "special-user-agent"
    )


def test_proxy_works_with_post():
    with requests_mock.Mocker() as m:
        m.post(
            "http://mock.dashboard/world",
            text='{"accepted": true}',
            headers={"content-type": "application/json"},
        )
        response = proxy.proxy_request(
            "http://mock.dashboard/world",
            {"user-agent": "special-user-agent", "content-type": "application/json"},
            '{"foo": "bar"}',
            {},
            "POST",
        )
    assert response.json["accepted"]
    assert m.request_history[0]._request.body == '{"foo": "bar"}'
