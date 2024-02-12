import pytest
from cf_auth_proxy.config import config_from_env


def test_config_loads(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "unit")
    config = config_from_env()
    assert config.DEBUG
    assert config.TESTING
    assert config.DASHBOARD_URL == "http://mock.dashboard/"
    assert config.UAA_AUTH_URL == "http://mock.uaa/authorize"
    assert config.UAA_TOKEN_URL == "http://mock.uaa/token"
    assert config.CF_API_URL == "http://mock.cf/"
    assert config.UAA_CLIENT_ID == "EXAMPLE"
    assert config.UAA_CLIENT_SECRET == "example"
    assert config.SECRET_KEY == "CHANGEME"
    assert config.PERMANENT_SESSION_LIFETIME == 120
    assert config.PERMITTED_SPACE_ROLES == [
        "space_developer",
        "space_manager",
        "space_auditor",
    ]
    assert config.PERMITTED_ORG_ROLES == [
        "organization_manager",
        "organization_auditor",
    ]
    assert config.CF_ADMIN_GROUP_NAME == "cloud_controller.admin"


@pytest.mark.parametrize(
    "dashboard_url", ["https://dashboard.example.com", "https://dashboard.example.com/"]
)
def test_local_config(monkeypatch, dashboard_url):
    monkeypatch.setenv("FLASK_ENV", "local")
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("DASHBOARD_URL", dashboard_url)
    monkeypatch.setenv("CF_API_URL", "https://api.example.com/")
    monkeypatch.setenv("UAA_AUTH_URL", "https://uaa.example.com/authorize")
    monkeypatch.setenv("UAA_BASE_URL", "https://uaa.example.com/")
    monkeypatch.setenv("UAA_CLIENT_ID", "feedabee")
    monkeypatch.setenv("UAA_CLIENT_SECRET", "CHANGEME")
    monkeypatch.setenv("SECRET_KEY", "changeme")
    monkeypatch.setenv("SESSION_LIFETIME", "3600")
    monkeypatch.setenv("CF_ADMIN_GROUP_NAME", "random-group")
    config = config_from_env()
    assert config.PORT == 8888
    assert config.DASHBOARD_URL == "https://dashboard.example.com/"
    assert config.DEBUG
    assert config.TESTING
    assert config.UAA_AUTH_URL == "https://uaa.example.com/authorize"
    assert config.UAA_BASE_URL == "https://uaa.example.com/"
    assert config.UAA_TOKEN_URL == "https://uaa.example.com/oauth/token"
    assert config.UAA_CLIENT_ID == "feedabee"
    assert config.UAA_CLIENT_SECRET == "CHANGEME"
    assert config.CF_API_URL == "https://api.example.com/"
    assert config.SECRET_KEY == "changeme"
    assert config.PERMANENT_SESSION_LIFETIME == 3600
    assert config.CF_ADMIN_GROUP_NAME == "random-group"


@pytest.mark.parametrize(
    "dashboard_url", ["https://dashboard.example.com", "https://dashboard.example.com/"]
)
def test_prod_config(monkeypatch, dashboard_url):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("PORT", "8888")
    monkeypatch.setenv("DASHBOARD_URL", dashboard_url)
    monkeypatch.setenv("UAA_AUTH_URL", "https://uaa.example.com/authorize")
    monkeypatch.setenv("UAA_BASE_URL", "https://uaa.example.com/")
    monkeypatch.setenv("CF_API_URL", "https://api.example.com/")
    monkeypatch.setenv("UAA_CLIENT_ID", "feedabee")
    monkeypatch.setenv("UAA_CLIENT_SECRET", "CHANGEME")
    monkeypatch.setenv("SECRET_KEY", "changeme")
    monkeypatch.setenv("SESSION_LIFETIME", "3600")
    monkeypatch.setenv("CF_ADMIN_GROUP_NAME", "random-group")
    config = config_from_env()
    assert config.PORT == 8888
    assert config.DASHBOARD_URL == "https://dashboard.example.com/"
    assert not config.DEBUG
    assert not config.TESTING
    assert config.UAA_AUTH_URL == "https://uaa.example.com/authorize"
    assert config.UAA_BASE_URL == "https://uaa.example.com/"
    assert config.UAA_TOKEN_URL == "https://uaa.example.com/oauth/token"
    assert config.UAA_CLIENT_ID == "feedabee"
    assert config.UAA_CLIENT_SECRET == "CHANGEME"
    assert config.CF_API_URL == "https://api.example.com/"
    assert config.SECRET_KEY == "changeme"
    assert config.PERMANENT_SESSION_LIFETIME == 3600
    assert config.PERMITTED_SPACE_ROLES == [
        "space_developer",
        "space_manager",
        "space_auditor",
    ]
    assert config.PERMITTED_ORG_ROLES == [
        "organization_manager",
        "organization_auditor",
    ]
    assert config.CF_ADMIN_GROUP_NAME == "random-group"
