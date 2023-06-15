from . import AUTH_PROXY_URL


def log_in(user, page, start_at=None):
    page.set_default_timeout(30000)
    if start_at is None:
        start_at = AUTH_PROXY_URL
    # go to opensearch dashboard
    page.goto(start_at)
    # accept the monitoring notice
    page.click(".island-button.js-notice-submit")
    # select the cloud.gov IdP
    page.click("a>span:has-text('cloud.gov')")
    page.fill("input[id='username']", user.username)
    page.fill("input[id='password']", user.password)
    page.click("text='Login'")
    page.fill("input[id='j_tokenNumber']", user.totp.now())
    page.click("text='Login'")
    # lots of redirects and stuff happen here, so just, like, chill, ok?
    page.wait_for_load_state("networkidle")
    if "/authorize?" in page.url:
        # first time using this app with this user
        page.click("text='Authorize'")
        page.wait_for_load_state("networkidle")

    # handle first-login stuff when it's here
    page.wait_for_timeout(1000)
    if "Start by adding your data" in page.content():
        page.click('text="Explore on my own"')


def switch_tenants(page, tenant="Global"):
    """
    switch to the specified tenant.
    """
    tenant_option = page.get_by_text(tenant)
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
    hamburger_button = page.locator(f"css=div.euiHeaderSectionItem.euiHeaderSectionItem--borderRight.header__toggleNavButtonSection")
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
