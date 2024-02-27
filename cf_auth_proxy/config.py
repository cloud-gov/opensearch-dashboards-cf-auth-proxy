from environs import Env


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
            "PERMITTED_ORG_ROLES", ["organization_manager", "organization_auditor"]
        )
        self.SESSION_COOKIE_NAME = "cfsession"
        # see https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
        self.REQUEST_TIMEOUT = 30


class UnitConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.DASHBOARD_URL = "http://mock.dashboard/"
        self.SESSION_TYPE = "filesystem"
        self.CF_API_URL = "http://mock.cf/"
        self.UAA_AUTH_URL = "http://mock.uaa/authorize"
        self.UAA_BASE_URL = "http://mock.uaa/"
        self.UAA_TOKEN_URL = "http://mock.uaa/token"  # nosec
        self.UAA_CLIENT_ID = "EXAMPLE"
        self.UAA_CLIENT_SECRET = "example"  # nosec
        self.SECRET_KEY = "CHANGEME"  # nosec
        self.PERMANENT_SESSION_LIFETIME = 120
        self.SESSION_REFRESH_EACH_REQUEST = False
        self.CF_ADMIN_GROUP_NAME = "cloud_controller.admin"
        self.DASHBOARD_CERTIFICATE = "fake-cert"
        self.DASHBOARD_CERTIFICATE_KEY = "fake-key"
        self.DASHBOARD_CERTIFICATE_CA = "fake-ca"


class LocalConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.DASHBOARD_URL = self.env_parser.str("DASHBOARD_URL")
        if self.DASHBOARD_URL[-1] != "/":
            self.DASHBOARD_URL = f"{self.DASHBOARD_URL}/"
        self.SESSION_TYPE = "filesystem"
        self.SESSION_COOKIE_SECURE = False

        self.SESSION_REFRESH_EACH_REQUEST = True

        self.CF_API_URL = self.env_parser("CF_API_URL")
        self.UAA_AUTH_URL = self.env_parser.str("UAA_AUTH_URL")
        self.UAA_BASE_URL = self.env_parser.str("UAA_BASE_URL")
        if self.UAA_BASE_URL[-1] != "/":
            self.UAA_BASE_URL = f"{self.UAA_BASE_URL}/"
        self.UAA_TOKEN_URL = f"{self.UAA_BASE_URL}oauth/token"
        self.UAA_CLIENT_ID = self.env_parser.str("UAA_CLIENT_ID")
        self.UAA_CLIENT_SECRET = self.env_parser.str("UAA_CLIENT_SECRET")
        self.SECRET_KEY = self.env_parser.str("SECRET_KEY")
        self.PERMANENT_SESSION_LIFETIME = self.env_parser.int("SESSION_LIFETIME")
        self.CF_ADMIN_GROUP_NAME = self.env_parser.str("CF_ADMIN_GROUP_NAME")
        self.DASHBOARD_CERTIFICATE = None
        self.DASHBOARD_CERTIFICATE_KEY = None
        self.DASHBOARD_CERTIFICATE_CA = None


class AppConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = False
        self.DEBUG = self.env_parser.bool("DEBUG", False)
        self.DASHBOARD_URL = self.env_parser.str("DASHBOARD_URL")
        if self.DASHBOARD_URL[-1] != "/":
            self.DASHBOARD_URL = f"{self.DASHBOARD_URL}/"
        self.SESSION_TYPE = "null"
        self.SESSION_COOKIE_SECURE = True

        self.CF_API_URL = self.env_parser("CF_API_URL")
        self.UAA_AUTH_URL = self.env_parser.str("UAA_AUTH_URL")
        self.UAA_BASE_URL = self.env_parser.str("UAA_BASE_URL")
        if self.UAA_BASE_URL[-1] != "/":
            self.UAA_BASE_URL = f"{self.UAA_BASE_URL}/"
        self.UAA_TOKEN_URL = f"{self.UAA_BASE_URL}oauth/token"
        self.UAA_CLIENT_ID = self.env_parser.str("UAA_CLIENT_ID")
        self.UAA_CLIENT_SECRET = self.env_parser.str("UAA_CLIENT_SECRET")
        self.SECRET_KEY = self.env_parser.str("SECRET_KEY")
        self.PERMANENT_SESSION_LIFETIME = self.env_parser.int("SESSION_LIFETIME")
        self.CF_ADMIN_GROUP_NAME = self.env_parser.str("CF_ADMIN_GROUP_NAME")
        self.DASHBOARD_CERTIFICATE = self.env_parser.str("DASHBOARD_CERTIFICATE")
        self.DASHBOARD_CERTIFICATE_KEY = self.env_parser.str(
            "DASHBOARD_CERTIFICATE_KEY"
        )
        self.DASHBOARD_CERTIFICATE_CA = self.env_parser.str("DASHBOARD_CERTIFICATE_CA")
