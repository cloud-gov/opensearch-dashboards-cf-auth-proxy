import pyotp


class User:
    def __init__(self, username, password, totp_seed, test_space_id, test_org_id):
        self.username = username
        self.password = password
        self.totp_seed = totp_seed
        self.test_space_id = test_space_id
        self.test_org_id = test_org_id
        self.totp = pyotp.TOTP(totp_seed)
