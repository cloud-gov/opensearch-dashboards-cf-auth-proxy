import pytest

from kibana_cf_auth_proxy.app import create_app


def pytest_configure(config):
    config.addinivalue_line("markers", "focus: Only run this test.")


def pytest_collection_modifyitems(items, config):
    """
    Focus on tests marked focus, if any.  Run all
    otherwise.
    """

    selected_items = []
    deselected_items = []

    focused = False

    for item in items:
        if item.get_closest_marker("focus"):
            focused = True
            selected_items.append(item)
        else:
            deselected_items.append(item)

    if focused:
        print("\nOnly running @pytest.mark.focus tests")
        config.hook.pytest_deselected(items=deselected_items)
        items[:] = selected_items


@pytest.fixture(scope="function")
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def authenticated_client(client):
    with client.session_transaction() as s:
        s["user"] = "me"
    yield client
