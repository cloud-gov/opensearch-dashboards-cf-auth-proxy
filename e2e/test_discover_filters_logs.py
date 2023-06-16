from .utils import log_in, switch_tenants, go_to_discover_page

def test_see_correct_logs_in_discover_tag(user_1, page):
    log_in(user=user_1, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    assert page.query_selector(".dscTimechart") is not None

    org_should_exist_results = page.query_selector_all("text=org_id_1")
    assert len(org_should_exist_results) >= 1

    space_should_exist_results = page.query_selector_all("text=space_id_1")
    assert len(space_should_exist_results) >= 1
    
    should_not_exist_results = page.query_selector_all("text=/(org|space)_id_2/")
    assert len(should_not_exist_results) == 0

def test_see_correct_logs_in_discover_tag_2(user_2, page):
    log_in(user=user_2, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    assert page.query_selector(".dscTimechart") is not None

    org_should_exist_results = page.query_selector_all("text=org_id_2")
    assert len(org_should_exist_results) >= 1
    space_should_exist_results = page.query_selector_all("text=space_id_2")
    assert len(space_should_exist_results) >= 1
    should_not_exist_results = page.query_selector_all("text=/(org|space)_id_1/")
    assert len(should_not_exist_results) == 0
