from environs import Env


def config_from_env():
    env = Env()
    if env.bool("LOCAL", False):
        return LocalConfig()
    return AppConfig()


class Config:
    def __init__(self):
        self.env_parser = Env()


class LocalConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True


class AppConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = False
        self.DEBUG = self.env_parser.bool("DEBUG", False)
