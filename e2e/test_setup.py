from . import KIBANA_URL
from .utils import log_in

import pytest


def test_redirects_to_login(page):
    page.goto(KIBANA_URL)
    assert "login" in page.url


def test_login(page, user_1):
    log_in(user_1, page)

    # this needs to get updated when we fix the callback to redirect
    assert page.url.startswith(f"{KIBANA_URL}cb?")
