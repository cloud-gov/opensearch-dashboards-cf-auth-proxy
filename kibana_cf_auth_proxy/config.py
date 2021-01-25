from environs import Env


def config_from_env():
    env = Env()
    environment_config = {"production": AppConfig, "local": LocalConfig}
    return environment_config[env("FLASK_ENV")]()


class Config:
    def __init__(self):
        self.env_parser = Env()
        self.PORT = self.env_parser.int("PORT", 8080)


class LocalConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.KIBANA_URL = "mock://kibana/"
        self.SESSION_TYPE = "filesystem"
        self.UAA_AUTH_URL = "mock://uaa/authorize"
        self.UAA_TOKEN_URL = "mock://uaa/token"
        self.UAA_REFRESH_URL = "mock://uaa/refresh"
        self.UAA_CLIENT_ID = "EXAMPLE"
        self.UAA_CLIENT_SECRET = "example"
        self.SECRET_KEY = "CHANGEME"


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

        self.UAA_AUTH_URL = self.env_parser.str("UAA_AUTH_URL")
        self.UAA_TOKEN_URL = self.env_parser.str("UAA_TOKEN_URL")
        self.UAA_REFRESH_URL = self.env_parser.str("UAA_REFRESH_URL")
        self.UAA_CLIENT_ID = self.env_parser.str("UAA_CLIENT_ID")
        self.UAA_CLIENT_SECRET = self.env_parser.str("UAA_CLIENT_SECRET")
        self.SECRET_KEY = self.env_parser.str("SECRET_KEY")
