import re

from . import AUTH_PROXY_URL


def log_in(user, page, start_at=None):
    page.set_default_timeout(60000)

    if start_at is None:
        start_at = AUTH_PROXY_URL

    # go to opensearch dashboard
    page.goto(start_at)

    # accept the monitoring notice
    agree_continue_button = page.get_by_text("AGREE AND CONTINUE")
    agree_continue_button.wait_for()
    agree_continue_button.click()

    # select the cloud.gov IdP
    cloud_gov_idp_button = page.get_by_role("link", name="cloud.gov")
    cloud_gov_idp_button.wait_for()
    cloud_gov_idp_button.click()

    username_field = page.get_by_label("Email address")
    password_field = page.get_by_label("Password")
    username_field.wait_for()
    password_field.wait_for()
    username_field.fill(user.username)
    password_field.fill(user.password)

    login_button = page.get_by_text("Login")
    login_button.wait_for()
    login_button.click()

    totp_field = page.locator("css=input[id='j_tokenNumber']")
    totp_field.wait_for()
    totp_field.fill(user.totp.now())

    login_button = page.get_by_text("Login")
    login_button.wait_for()
    login_button.click()

    # lots of redirects and stuff happen here, so just, like, chill, ok?
    page.wait_for_load_state("networkidle")

    if "/authorize?" in page.url:
        # first time using this app with this user
        authorize_button = page.get_by_text("Authorize")
        authorize_button.wait_for()
        authorize_button.click()
        page.wait_for_load_state("networkidle")

    page.wait_for_url(f"{AUTH_PROXY_URL}*")

    # handle first-login stuff when it's here
    page.wait_for_timeout(5000)

    if page.get_by_text("Start by adding your data").is_visible():
        explore_button = page.get_by_text("Explore on my own")
        explore_button.wait_for()
        explore_button.click()


def switch_tenants(page, tenant="Global"):
    """
    switch to the specified tenant.
    """
    tenant_option = page.get_by_text(re.compile(f"^{tenant}.*$"))
    tenant_option.wait_for()
    tenant_option.click()

    # submit
    submit_button = page.get_by_text("Confirm")
    submit_button.wait_for()
    submit_button.click()

    # todo: there is a page refresh that happens after submitting the tenant option.
    # we should wait on an element instead of arbitrary timeout
    page.wait_for_timeout(2000)


def go_to_discover_page(page):
    # open the hamburger menu
    hamburger_button = page.locator(
        f"css=div.euiHeaderSectionItem.euiHeaderSectionItem--borderRight.header__toggleNavButtonSection"
    )
    hamburger_button.wait_for()
    hamburger_button.click()

    # go to the discover page
    discover_menu_link = page.get_by_text("Discover")
    discover_menu_link.wait_for()
    discover_menu_link.click()

    # wait for the refresh button, signifying the discover page has loaded
    refresh_button = page.get_by_text("Refresh")
    refresh_button.wait_for()

    # the box the results are in
    content_box = page.locator("css=div.dscWrapper__content")
    content_box.wait_for()
