from . import KIBANA_URL
from .utils import log_in, switch_tenants


def test_see_correct_logs_in_discover_tag(user_1, page):
    log_in(user=user_1, page=page)

    page.goto(KIBANA_URL, wait_until="networkidle")
    switch_tenants(page)

    # open the hamburger menu
    page.click(
        "div.euiHeaderSectionItem.euiHeaderSectionItem--borderRight.header__toggleNavButtonSection"
    )
    # go to the discover page
    page.click("text=Discover")

    # wait for the refresh button, signifying the discover page has loaded
    page.wait_for_selector('button:has-text("Refresh")')
    # the box the results are in
    page.wait_for_selector("div.dscWrapper__content")
    assert page.query_selector(".dscTimechart") is not None

    org_should_exist_results = page.query_selector_all("text=org_id_1")
    assert len(org_should_exist_results) >= 1
    space_should_exist_results = page.query_selector_all("text=space_id_1")
    assert len(space_should_exist_results) >= 1
    should_not_exist_results = page.query_selector_all("text=/(org|space)_id_2/")
    assert len(should_not_exist_results) == 0
