from . import KIBANA_URL

import time

def test_redirects_to_login(page):
    page.goto(KIBANA_URL)
    assert "login" in page.url


def test_login(page, user_1):
    # go to kibana
    page.goto(KIBANA_URL)
    # accept the monitoring notice
    page.click(".island-button.js-notice-submit")
    # select the cloud.gov IdP
    page.click("a>span:has-text('cloud.gov')")
    page.fill("input[id='username']", user_1.username)
    page.fill("input[id='password']", user_1.password)
    page.click("text='Login'")
    page.fill("input[id='j_tokenNumber']", user_1.totp.now())
    page.click("text='Login'")
    # lots of redirects and stuff happen here, so just, like, chill, ok?
    page.wait_for_load_state("networkidle")
    if "/authorize?" in page.url:
        # first time using this app with this user
        page.click("text='Authorize'")

    # this needs to get updated when we fix the callback to redirect
    assert page.url.startswith(f"{KIBANA_URL}cb?")
