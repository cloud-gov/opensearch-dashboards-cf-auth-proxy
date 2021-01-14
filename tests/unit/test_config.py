import pytest
from kibana_cf_auth_proxy.config import config_from_env


def test_config_loads(monkeypatch):
    monkeypatch.setenv("LOCAL", "true")
    config = config_from_env()
    assert config.DEBUG
    assert config.TESTING


def test_prod_config_does_not_set_debug(monkeypatch):
    config = config_from_env()
    assert not config.DEBUG
    assert not config.TESTING
