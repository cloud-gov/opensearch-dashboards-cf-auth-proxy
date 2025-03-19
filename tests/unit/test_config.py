import json

import jwcrypto
import pytest

from cf_auth_proxy.config import config_from_env


@pytest.fixture()
def base_local_config(monkeypatch, token_keys):
    # set all the required variables with values that hint that they're
    # not what we want
    monkeypatch.setenv("CF_API_URL", "https://wrong-value.example.com/")
    monkeypatch.setenv("UAA_AUTH_URL", "https://wrong-value.example.com/authorize")
    monkeypatch.setenv("UAA_BASE_URL", "https://wrong-value.example.com/")
    monkeypatch.setenv("DASHBOARD_URL", "https://wrong-value.example.com/")
    monkeypatch.setenv("SECRET_KEY", "CHANGEME")
    monkeypatch.setenv("SESSION_LIFETIME", "1")
    monkeypatch.setenv("UAA_CLIENT_ID", "CHANGEME")
    monkeypatch.setenv("UAA_CLIENT_SECRET", "CHANGEME")
    monkeypatch.setenv("UAA_JWKS", '{"keys":[]}')
    monkeypatch.setenv("CF_ADMIN_GROUP_NAME", "wrong-value")
    monkeypatch.setenv("CF_AUDITOR_GROUP_NAME", "wrong-value")
    monkeypatch.setenv("DASHBOARD_URL", "https://wrong-value.example.com/")
    monkeypatch.setenv("FLASK_ENV", "local")
    monkeypatch.setenv("REDIS_HOST", "fake-redis-host")


@pytest.fixture
def token_keys() -> str:
    def make_key(name):
        key_type = "RSA"
        alg = "RS256"
        use = "sig"
        return jwcrypto.jwk.JWK.generate(
            kty=key_type, size=2048, kid=name, use=use, alg=alg
        )

    keyset = jwcrypto.jwk.JWKSet()
    keyset.add(make_key("key-0"))
    keyset.add(make_key("key-1"))
    key_dict = keyset.export(as_dict=True)

    # UAA includes the PEM of each key as `value` in the JWK
    # and pyJWT is easier to use with PEM, so we inject it here
    key_dict["keys"][0]["value"] = str(keyset.get_key("key-0").export_to_pem().decode())
    key_dict["keys"][1]["value"] = str(keyset.get_key("key-1").export_to_pem().decode())

    return key_dict


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
    assert config.ORG_ROLE == [
        "organization_user",
    ]
    assert config.CF_ADMIN_GROUP_NAME == "cloud_controller.admin"
    assert config.CF_AUDITOR_GROUP_NAME == "cloud_controller.global_auditor"
    assert config.REQUEST_TIMEOUT == 30

    assert config.REQUEST_TIMEOUT == 30


@pytest.mark.parametrize(
    "dashboard_url", ["https://dashboard.example.com", "https://dashboard.example.com/"]
)
def test_config_sets_dashboard_url(monkeypatch, base_local_config, dashboard_url):
    monkeypatch.setenv("DASHBOARD_URL", dashboard_url)
    config = config_from_env()
    assert config.DASHBOARD_URL == "https://dashboard.example.com/"


@pytest.mark.parametrize(
    "env,is_local_testing",
    [pytest.param("local", True), pytest.param("production", False)],
)
def test_env_config_sets_debug_testing(
    monkeypatch, base_local_config, env, is_local_testing
):
    monkeypatch.setenv("FLASK_ENV", env)
    config = config_from_env()
    assert config.DEBUG == is_local_testing
    assert config.TESTING == is_local_testing


def test_prod_has_secure_settings(monkeypatch, base_local_config):
    monkeypatch.setenv("FLASK_ENV", "production")
    config = config_from_env()

    assert config.SESSION_TYPE == "redis"
    assert config.SESSION_COOKIE_SECURE
    assert config.SESSION_REDIS


def test_local_has_test_friendly_settings(monkeypatch, base_local_config):
    monkeypatch.setenv("FLASK_ENV", "local")
    config = config_from_env()

    assert not config.SESSION_COOKIE_SECURE


def test_config_sets_port(monkeypatch, base_local_config):
    monkeypatch.setenv("PORT", "8888")
    config = config_from_env()
    assert config.PORT == 8888


def test_config_gets_urls(monkeypatch, base_local_config):
    monkeypatch.setenv("CF_API_URL", "https://api.example.com/")
    monkeypatch.setenv("UAA_AUTH_URL", "https://uaa.example.com/authorize")
    monkeypatch.setenv("UAA_BASE_URL", "https://uaa.example.com/")
    config = config_from_env()
    assert config.UAA_AUTH_URL == "https://uaa.example.com/authorize"
    assert config.UAA_BASE_URL == "https://uaa.example.com/"
    assert config.UAA_TOKEN_URL == "https://uaa.example.com/oauth/token"


def test_config_gets_uaa_credentials(monkeypatch, base_local_config):
    monkeypatch.setenv("UAA_CLIENT_ID", "feedabee")
    monkeypatch.setenv("UAA_CLIENT_SECRET", "FEEDABEE")
    config = config_from_env()
    assert config.UAA_CLIENT_ID == "feedabee"
    assert config.UAA_CLIENT_SECRET == "FEEDABEE"


def test_config_sets_secret_key(monkeypatch, base_local_config):
    monkeypatch.setenv("SECRET_KEY", "feedabee")
    monkeypatch.setenv("DASHBOARD_URL", "https://dashboard.example.com/")
    config = config_from_env()
    assert config.SECRET_KEY == "feedabee"


def test_config_sets_session_lifetime(monkeypatch, base_local_config):
    monkeypatch.setenv("SESSION_LIFETIME", "3600")
    config = config_from_env()
    assert config.PERMANENT_SESSION_LIFETIME == 3600


def test_config_sets_admin_group(monkeypatch, base_local_config):
    monkeypatch.setenv("CF_ADMIN_GROUP_NAME", "random-group")
    config = config_from_env()
    assert config.CF_ADMIN_GROUP_NAME == "random-group"


def test_config_sets_auditor_group(monkeypatch, base_local_config):
    monkeypatch.setenv("CF_AUDITOR_GROUP_NAME", "random-group")
    config = config_from_env()
    assert config.CF_AUDITOR_GROUP_NAME == "random-group"


def test_config_sets_uaa_jwks(monkeypatch, base_local_config, token_keys):
    monkeypatch.setenv("UAA_JWKS", json.dumps(token_keys))
    monkeypatch.setenv("FLASK_ENV", "local")
    monkeypatch.setenv("DASHBOARD_URL", "https://dashboard.example.com/")
    config = config_from_env()
    assert isinstance(config.UAA_JWKS, jwcrypto.jwk.JWKSet)
    key0 = config.UAA_JWKS.get_key("key-0")
    key1 = config.UAA_JWKS.get_key("key-1")

    # we normally just trust that the libraries we're using do the right thing
    # this check is because the `value` property that UAA provides is not expected
    # by jwcrypto, so we want to make sure it doesn't break the JKWS and that it
    # comes through in the values
    assert key0 is not None
    assert "BEGIN PUBLIC KEY" in key0["value"]
    assert key1 is not None
    assert "BEGIN PUBLIC KEY" in key1["value"]
