from playwright.sync_api import expect
from .utils import log_in, switch_tenants, go_to_discover_page, get_user_menu


def test_see_correct_logs_in_discover_user_1(user_1, page):
    log_in(user=user_1, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    expect(page.get_by_text("1 hit")).to_be_visible()
    expect(page.get_by_text("org_id_1")).not_to_be_visible()
    expect(page.get_by_text("org_id_2")).not_to_be_visible()
    expect(page.get_by_text("space_id_1")).to_be_visible()
    expect(page.get_by_text("space_id_2")).not_to_be_visible()
    expect(page.get_by_text("org_1_both_orgs_space")).not_to_be_visible()
    expect(page.get_by_text("org_2_both_orgs_space")).not_to_be_visible()

    get_user_menu(user=user_1, page=page)
    expect(page.get_by_text(user_1.username)).to_be_visible()


def test_see_correct_logs_in_discover_user_2(user_2, page):
    log_in(user=user_2, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    expect(page.get_by_text("3 hits")).to_be_visible()
    expect(page.get_by_text("org_id_1")).not_to_be_visible()
    expect(page.get_by_text("org_id_2")).to_be_visible()
    expect(page.get_by_text("space_id_1")).not_to_be_visible()
    expect(page.get_by_text("space_id_2")).to_be_visible()
    expect(page.get_by_text("org_1_both_orgs_space")).not_to_be_visible()
    expect(page.get_by_text("org_2_both_orgs_space")).to_be_visible()

    get_user_menu(user=user_2, page=page)
    expect(page.get_by_text(user_2.username)).to_be_visible()

def test_see_correct_logs_in_discover_user_3(user_3, page):
    log_in(user=user_3, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    expect(page.get_by_text("2 hits")).to_be_visible()
    expect(page.get_by_text("org_id_1")).not_to_be_visible()
    expect(page.get_by_text("org_id_2")).not_to_be_visible()
    expect(page.get_by_text("space_id_1")).to_be_visible()
    expect(page.get_by_text("space_id_2")).to_be_visible()
    expect(page.get_by_text("org_1_both_orgs_space")).not_to_be_visible()
    expect(page.get_by_text("org_2_both_orgs_space")).not_to_be_visible()

    get_user_menu(user=user_3, page=page)
    expect(page.get_by_text(user_3.username)).to_be_visible()

def test_see_correct_logs_in_discover_user_4(user_4, page):
    log_in(user=user_4, page=page)

    switch_tenants(page)

    go_to_discover_page(page)

    expect(page.get_by_text("1 hit")).to_be_visible()
    expect(page.get_by_text("org_id_1")).not_to_be_visible()
    expect(page.get_by_text("org_id_2")).not_to_be_visible()
    expect(page.get_by_text("space_id_1")).not_to_be_visible()
    expect(page.get_by_text("space_id_2")).not_to_be_visible()
    expect(page.get_by_text("org_1_both_orgs_space")).to_be_visible()
    expect(page.get_by_text("org_2_both_orgs_space")).not_to_be_visible()

    get_user_menu(user=user_4, page=page)
    expect(page.get_by_text(user_4.username)).to_be_visible()
