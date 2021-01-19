import pytest
from kibana_cf_auth_proxy.config import config_from_env


def test_config_loads(monkeypatch):
    monkeypatch.setenv("LOCAL", "true")
    config = config_from_env()
    assert config.DEBUG
    assert config.TESTING
    assert config.KIBANA_URL == "mock://kibana"


def test_prod_config(monkeypatch):
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("KIBANA_URL", "https://foo.bar.baz")
    config = config_from_env()
    assert config.PORT == 8888
    assert config.KIBANA_URL == "https://foo.bar.baz"
    assert not config.DEBUG
    assert not config.TESTING

