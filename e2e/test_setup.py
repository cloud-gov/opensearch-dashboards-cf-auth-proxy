import re
from playwright.sync_api import expect
from urllib.parse import urljoin
from . import AUTH_PROXY_URL
from .utils import log_in


def test_redirects_to_login(page):
    page.goto(AUTH_PROXY_URL)
    expect(page).to_have_url(re.compile(".*login.*"))


def test_login_redirects_home_without_slash(page, user_1):
    # this tests an actual bug where going to the home page without
    # a trailing slash (e.g. logs.example.com) causes a redirect
    # to an invalid endpoint.
    log_in(user_1, page, str.rstrip(AUTH_PROXY_URL, "/"))
    expect(page).to_have_url(re.compile(f"{urljoin(AUTH_PROXY_URL, 'app/home')}.*"))


def test_login_redirects_home(page, user_1):
    # this tests the basic case - going to logs.example.com/
    log_in(user_1, page)
    expect(page).to_have_url(re.compile(f"{urljoin(AUTH_PROXY_URL, 'app/home')}.*"))


def test_login_remembers_target(page, user_1):
    log_in(user_1, page, urljoin(AUTH_PROXY_URL, "app/dev_tools"))
    expect(page).to_have_url(
        re.compile(f"{urljoin(AUTH_PROXY_URL, 'app/dev_tools')}.*")
    )
