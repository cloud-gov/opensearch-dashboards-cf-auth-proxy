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
    Must start on a page with the user menu accessible.
    """
    # open the user menu
    #page.click("id=actionsMenu")
    #page.wait_for_load_state("networkidle")
    # open the switch tenant pane
    #page.click("text=Switch tenants")
    #page.wait_for_load_state("networkidle")
    # select the global tenant
    page.click(f"text={tenant}")
    page.wait_for_load_state("networkidle")
    # submit
    page.click("text=Confirm")
    page.wait_for_load_state("networkidle")

    # this page takes a few seconds, but playwright doesn't seem to think anything is happening
    # todo: find a better thing to wait for here.
    page.wait_for_timeout(2000)
