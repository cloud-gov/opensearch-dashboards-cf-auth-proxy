import pytest
from kibana_cf_auth_proxy.config import config_from_env


def test_config_loads(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "local")
    config = config_from_env()
    assert config.DEBUG
    assert config.TESTING
    assert config.KIBANA_URL == "mock://kibana/"
    assert config.UAA_AUTH_URL == "mock://uaa/authorize"
    assert config.UAA_TOKEN_URL == "mock://uaa/token"
    assert config.UAA_REFRESH_URL == "mock://uaa/refresh"
    assert config.UAA_CLIENT_ID == "EXAMPLE"
    assert config.UAA_CLIENT_SECRET == "example"
    assert config.SECRET_KEY == "CHANGEME"


@pytest.mark.parametrize(
    "kibana_url", ["https://kibana.example.com", "https://kibana.example.com/"]
)
def test_prod_config(monkeypatch, kibana_url):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("KIBANA_URL", kibana_url)
    monkeypatch.setenv("UAA_AUTH_URL", "https://uaa.example.com/authorize")
    monkeypatch.setenv("UAA_TOKEN_URL", "https://uaa.example.com/token")
    monkeypatch.setenv("UAA_REFRESH_URL", "https://uaa.example.com/refresh")
    monkeypatch.setenv("UAA_CLIENT_ID", "feedabee")
    monkeypatch.setenv("UAA_CLIENT_SECRET", "CHANGEME")
    monkeypatch.setenv("SECRET_KEY", "changeme")
    config = config_from_env()
    assert config.PORT == 8888
    assert config.KIBANA_URL == "https://kibana.example.com/"
    assert not config.DEBUG
    assert not config.TESTING
    assert config.UAA_AUTH_URL == "https://uaa.example.com/authorize"
    assert config.UAA_TOKEN_URL == "https://uaa.example.com/token"
    assert config.UAA_REFRESH_URL == "https://uaa.example.com/refresh"
    assert config.UAA_CLIENT_ID == "feedabee"
    assert config.UAA_CLIENT_SECRET == "CHANGEME"
    assert config.SECRET_KEY == "changeme"
