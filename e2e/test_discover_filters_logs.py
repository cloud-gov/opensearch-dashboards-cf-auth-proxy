from .utils import log_in, switch_tenants, go_to_discover_page


def test_see_correct_logs_in_discover_user_1(user_1, page):
    log_in(user=user_1, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    assert page.get_by_text("1 hit").count() == 1
    assert page.get_by_text("org_id_1").count() == 0
    assert page.get_by_text("org_id_2").count() == 0
    assert page.get_by_text("space_id_1").count() == 1
    assert page.get_by_text("space_id_2").count() == 0
    assert page.get_by_text("org_1_both_orgs_space").count() == 0
    assert page.get_by_text("org_2_both_orgs_space").count() == 0


def test_see_correct_logs_in_discover_user_2(user_2, page):
    log_in(user=user_2, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    assert page.get_by_text("3 hits").count() == 1
    assert page.get_by_text("org_id_1").count() == 0
    assert page.get_by_text("org_id_2").count() == 1
    assert page.get_by_text("space_id_1").count() == 0
    assert page.get_by_text("space_id_2").count() == 1
    assert page.get_by_text("org_1_both_orgs_space").count() == 0
    assert page.get_by_text("org_2_both_orgs_space").count() == 1


def test_see_correct_logs_in_discover_user_3(user_3, page):
    log_in(user=user_3, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    assert page.get_by_text("2 hits").count() == 1
    assert page.get_by_text("org_id_1").count() == 0
    assert page.get_by_text("org_id_2").count() == 0
    assert page.get_by_text("space_id_1").count() == 1
    assert page.get_by_text("space_id_2").count() == 1
    assert page.get_by_text("org_1_both_orgs_space").count() == 0
    assert page.get_by_text("org_2_both_orgs_space").count() == 0


def test_see_correct_logs_in_discover_user_4(user_4, page):
    log_in(user=user_4, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    assert page.get_by_text("1 hit").count() == 1
    assert page.get_by_text("org_id_1").count() == 0
    assert page.get_by_text("org_id_2").count() == 0
    assert page.get_by_text("space_id_1").count() == 0
    assert page.get_by_text("space_id_2").count() == 0
    assert page.get_by_text("org_1_both_orgs_space").count() == 1
    assert page.get_by_text("org_2_both_orgs_space").count() == 0
