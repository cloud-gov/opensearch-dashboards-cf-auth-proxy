from . import KIBANA_URL
from .utils import log_in

import pytest


def test_redirects_to_login(page):
    page.goto(KIBANA_URL)
    assert "login" in page.url


def test_login_redirects_home_without_slash(page, user_1):
    # this tests an actual bug where going to the home page without (e.g. logs.example.com)
    # a trailing slash causes a redirect to an invalid endpoint.
    log_in(user_1, page, KIBANA_URL[:-1])
    assert page.url.startswith(f"{KIBANA_URL}app/home")


def test_login_redirects_home(page, user_1):
    # this tests the basic case - going to logs.example.com/ 
    log_in(user_1, page)
    assert page.url.startswith(f"{KIBANA_URL}app/home")


def test_login_remembers_target(page, user_1):
    log_in(user_1, page, f'{KIBANA_URL}app/dev_tools')
    assert page.url.startswith(f"{KIBANA_URL}app/dev_tools")
