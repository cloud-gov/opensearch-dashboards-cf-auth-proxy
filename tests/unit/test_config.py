import pytest
from kibana_cf_auth_proxy.config import config_from_env


def test_config_loads(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "local")
    config = config_from_env()
    assert config.DEBUG
    assert config.TESTING
    assert config.KIBANA_URL == "mock://kibana/"


@pytest.mark.parametrize("kibana_url", ["https://foo.bar.baz", "https://foo.bar.baz/"])
def test_prod_config(monkeypatch, kibana_url):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("KIBANA_URL", kibana_url)
    config = config_from_env()
    assert config.PORT == 8888
    assert config.KIBANA_URL == "https://foo.bar.baz/"
    assert not config.DEBUG
    assert not config.TESTING

