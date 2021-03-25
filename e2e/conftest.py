from os import getenv

import pytest

from .user import User


@pytest.fixture
def user_1():
    user_1_username = getenv(f"DEV_TEST_USER_1_USERNAME")
    user_1_password = getenv(f"DEV_TEST_USER_1_PASSWORD")
    user_1_totp_seed = getenv(f"DEV_TEST_USER_1_TOTP_SEED")
    user_1_space_id = getenv(f"DEV_TEST_USER_1_SPACE_ID")
    user_1_org_id = getenv(f"DEV_TEST_USER_1_ORG_ID")
    user_1 = User(
        user_1_username,
        user_1_password,
        user_1_totp_seed,
        user_1_space_id,
        user_1_org_id,
    )
    return user_1


@pytest.fixture
def user_2():
    user_2_username = getenv(f"DEV_TEST_USER_2_USERNAME")
    user_2_password = getenv(f"DEV_TEST_USER_2_PASSWORD")
    user_2_totp_seed = getenv(f"DEV_TEST_USER_2_TOTP_SEED")
    user_2_space_id = getenv(f"DEV_TEST_USER_2_SPACE_ID")
    user_2_org_id = getenv(f"DEV_TEST_USER_2_ORG_ID")
    user_2 = User(
        user_2_username,
        user_2_password,
        user_2_totp_seed,
        user_2_space_id,
        user_2_org_id,
    )
    return user_2
