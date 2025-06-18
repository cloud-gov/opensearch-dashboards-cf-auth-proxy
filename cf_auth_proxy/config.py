import json
from redis import Redis

from environs import Env
from jwcrypto import jwk


def config_from_env():
    env = Env()
    environment_config = {
        "production": AppConfig,
        "unit": UnitConfig,
        "local": LocalConfig,
    }
    return environment_config[env("FLASK_ENV")]()


class Config:
    def __init__(self):
        self.env_parser = Env()
        self.PORT = self.env_parser.int("PORT", 8080)
        self.PERMITTED_SPACE_ROLES = self.env_parser.list(
            "PERMITTED_SPACE_ROLES",
            ["space_developer", "space_manager", "space_auditor"],
        )
        self.PERMITTED_ORG_ROLES = self.env_parser.list(
            "PERMITTED_ORG_ROLES",
            ["organization_manager", "organization_auditor"],
        )
        self.ORG_ROLE = self.env_parser.list(
            "ORG_ROLE",
            ["organization_user"],
        )
        self.SESSION_COOKIE_NAME = "opensearch_proxy_session"
        # see https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
        self.REQUEST_TIMEOUT = 30


class UnitConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.DASHBOARD_URL = "http://mock.dashboard/"
        self.OPENSEARCH_URL = "http://mock.opensearch/"
        self.SESSION_TYPE = "filesystem"
        self.CF_API_URL = "http://mock.cf/"
        self.UAA_AUTH_URL = "http://mock.uaa/authorize"
        self.UAA_BASE_URL = "http://mock.uaa/"
        self.UAA_TOKEN_URL = "http://mock.uaa/token"  # nosec
        self.UAA_CLIENT_ID = "EXAMPLE"
        self.UAA_CLIENT_SECRET = "example"  # nosec
        self.SECRET_KEY = "CHANGEME"  # nosec
        self.PERMANENT_SESSION_LIFETIME = 120
        self.CF_ADMIN_GROUP_NAME = "cloud_controller.admin"
        self.CF_AUDITOR_GROUP_NAME = "cloud_controller.global_auditor"
        self.DASHBOARD_CERTIFICATE = "fake-cert"
        self.DASHBOARD_CERTIFICATE_KEY = "fake-key"
        self.DASHBOARD_CERTIFICATE_CA = "fake-ca"
        self.OPENSEARCH_CERTIFICATE = "fake-cert"
        self.OPENSEARCH_CERTIFICATE_KEY = "fake-key"
        self.OPENSEARCH_CERTIFICATE_CA = "fake-ca"
        keys = [
            jwk.JWK.generate(kty="RSA", size=2048, kid=name, use="sig", alg="RS256")
            for name in ("key-0", "key-1")
        ]
        keyset = jwk.JWKSet()
        keyset.add(keys[0])
        keyset.add(keys[1])
        key_dict = keyset.export(as_dict=True)

        # UAA includes the PEM of each key as `value` in the JWK
        # and pyJWT is easier to use with PEM, so we inject it here
        key_dict["keys"][0]["value"] = str(keys[0].export_to_pem().decode())
        key_dict["keys"][1]["value"] = str(keys[1].export_to_pem().decode())
        jwks_str = json.dumps(key_dict)

        # this is so we can _sign_ using these keys without creating fixtures
        self.LOCAL_KEYPAIR = keys

        # we're dumping and reloading to make sure we end up with a similar object to prod
        self.UAA_JWKS = jwk.JWKSet.from_json(jwks_str)


class AppConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = False
        self.DEBUG = self.env_parser.bool("DEBUG", False)
        self.DASHBOARD_URL = self.env_parser.str("DASHBOARD_URL")
        if self.DASHBOARD_URL[-1] != "/":
            self.DASHBOARD_URL = f"{self.DASHBOARD_URL}/"
        self.OPENSEARCH_URL = self.env_parser.str("OPENSEARCH_URL")
        if self.OPENSEARCH_URL[-1] != "/":
            self.OPENSEARCH_URL = f"{self.OPENSEARCH_URL}/"
        self.SESSION_TYPE = "redis"
        self.SESSION_REDIS = Redis(
            host=self.env_parser.str("REDIS_HOST"),
            port=6379,
            password=self.env_parser.str("REDIS_PASSWORD", None),
            ssl=True,
        )
        self.SESSION_COOKIE_SECURE = True
        self.PERMANENT_SESSION_LIFETIME = self.env_parser.int("SESSION_LIFETIME")

        self.CF_API_URL = self.env_parser("CF_API_URL")
        self.UAA_AUTH_URL = self.env_parser.str("UAA_AUTH_URL")
        self.UAA_BASE_URL = self.env_parser.str("UAA_BASE_URL")
        if self.UAA_BASE_URL[-1] != "/":
            self.UAA_BASE_URL = f"{self.UAA_BASE_URL}/"
        self.UAA_TOKEN_URL = f"{self.UAA_BASE_URL}oauth/token"
        self.UAA_CLIENT_ID = self.env_parser.str("UAA_CLIENT_ID")
        self.UAA_CLIENT_SECRET = self.env_parser.str("UAA_CLIENT_SECRET")
        self.SECRET_KEY = self.env_parser.str("SECRET_KEY")
        self.CF_ADMIN_GROUP_NAME = self.env_parser.str("CF_ADMIN_GROUP_NAME")
        self.CF_AUDITOR_GROUP_NAME = self.env_parser.str("CF_AUDITOR_GROUP_NAME")
        self.DASHBOARD_CERTIFICATE = self.env_parser.str("DASHBOARD_CERTIFICATE", None)
        self.DASHBOARD_CERTIFICATE_KEY = self.env_parser.str(
            "DASHBOARD_CERTIFICATE_KEY", None
        )
        self.DASHBOARD_CERTIFICATE_CA = self.env_parser.str(
            "DASHBOARD_CERTIFICATE_CA", None
        )
        self.OPENSEARCH_CERTIFICATE = self.env_parser.str(
            "OPENSEARCH_CERTIFICATE", None
        )
        self.OPENSEARCH_CERTIFICATE_KEY = self.env_parser.str(
            "OPENSEARCH_CERTIFICATE_KEY", None
        )
        self.OPENSEARCH_CERTIFICATE_CA = self.env_parser.str(
            "OPENSEARCH_CERTIFICATE_CA", None
        )
        jwks_jose = self.env_parser.str("UAA_JWKS")
        self.UAA_JWKS = jwk.JWKSet.from_json(jwks_jose)


class LocalConfig(AppConfig):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.SESSION_COOKIE_SECURE = False
        self.SESSION_REDIS = Redis(
            host=self.env_parser.str("REDIS_HOST"),
            port=6379,
        )
