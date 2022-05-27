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


class UnitConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.KIBANA_URL = "mock://kibana/"
        self.SESSION_TYPE = "filesystem"
        self.CF_API_URL = "mock://cf/"
        self.UAA_AUTH_URL = "mock://uaa/authorize"
        self.UAA_BASE_URL = "mock://uaa/"
        self.UAA_TOKEN_URL = "mock://uaa/token"
        self.UAA_CLIENT_ID = "EXAMPLE"
        self.UAA_CLIENT_SECRET = "example"
        self.SECRET_KEY = "CHANGEME"
        self.PERMANENT_SESSION_LIFETIME = 120
        self.SESSION_REFRESH_EACH_REQUEST = False


class LocalConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.KIBANA_URL = self.env_parser.str("KIBANA_URL")
        if self.KIBANA_URL[-1] != "/":
            self.KIBANA_URL = f"{self.KIBANA_URL}/"
        self.SESSION_TYPE = "filesystem"
        self.SESSION_COOKIE_SECURE = False

        self.SESSION_REFRESH_EACH_REQUEST = True

        self.CF_API_URL = self.env_parser("CF_API_URL")
        self.UAA_AUTH_URL = self.env_parser.str("UAA_AUTH_URL")
        self.UAA_BASE_URL = self.env_parser.str("UAA_BASE_URL")
        self.UAA_TOKEN_URL = self.env_parser.str("UAA_TOKEN_URL")
        self.UAA_CLIENT_ID = self.env_parser.str("UAA_CLIENT_ID")
        self.UAA_CLIENT_SECRET = self.env_parser.str("UAA_CLIENT_SECRET")
        self.SECRET_KEY = self.env_parser.str("SECRET_KEY")
        self.PERMANENT_SESSION_LIFETIME = self.env_parser.int("SESSION_LIFETIME")


class AppConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = False
        self.DEBUG = self.env_parser.bool("DEBUG", False)
        self.KIBANA_URL = self.env_parser.str("KIBANA_URL")
        if self.KIBANA_URL[-1] != "/":
            self.KIBANA_URL = f"{self.KIBANA_URL}/"
        self.SESSION_TYPE = "null"
        self.SESSION_COOKIE_SECURE = True

        self.CF_API_URL = self.env_parser("CF_API_URL")
        self.UAA_AUTH_URL = self.env_parser.str("UAA_AUTH_URL")
        self.UAA_BASE_URL = self.env_parser.str("UAA_BASE_URL")
        self.UAA_TOKEN_URL = self.env_parser.str("UAA_TOKEN_URL")
        self.UAA_CLIENT_ID = self.env_parser.str("UAA_CLIENT_ID")
        self.UAA_CLIENT_SECRET = self.env_parser.str("UAA_CLIENT_SECRET")
        self.SECRET_KEY = self.env_parser.str("SECRET_KEY")
        self.PERMANENT_SESSION_LIFETIME = self.env_parser.int("SESSION_LIFETIME")
