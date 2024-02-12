import pytest

from cf_auth_proxy.app import create_app


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
        s["user_id"] = "me"
    yield client


@pytest.fixture()
def simple_space_response():
    return """
  {
   "pagination": {
      "total_results": 1,
      "total_pages": 1,
      "first": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=space_developer%2Cspace_manager&user_guids=a-user-guid"
      },
      "last": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=space_developer%2Cspace_manager&user_guids=a-user-guid"
      },
      "next": null,
      "previous": null
   },
   "resources": [
      {
         "guid": "role-guid-1",
         "created_at": "2019-12-12T18:59:12Z",
         "updated_at": "2019-12-12T18:59:13Z",
         "type": "space_developer",
         "relationships": {
            "user": {
               "data": {
                  "guid": "a-user-guid"
               }
            },
            "space": {
               "data": {
                  "guid": "space-guid-1"
               }
            },
            "organization": {
               "data": null
            }
         },
         "links": {
            "self": {
               "href": "http://mock.cf/v3/roles/role-guid-1"
            },
            "user": {
               "href": "http://mock.cf/v3/users/a-user-guid"
            },
            "space": {
               "href": "http://mock.cf/v3/spaces/space-guid-1"
            }
         }
        }
      ]
    } """


@pytest.fixture()
def simple_org_response():
    return """
  {
   "pagination": {
      "total_results": 1,
      "total_pages": 1,
      "first": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=org_manager&user_guids=a-user-guid"
      },
      "last": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=org_manager&user_guids=a-user-guid"
      },
      "next": null,
      "previous": null
   },
   "resources": [
      {
         "guid": "role-guid-1",
         "created_at": "2019-12-12T18:59:12Z",
         "updated_at": "2019-12-12T18:59:13Z",
         "type": "space_developer",
         "relationships": {
            "user": {
               "data": {
                  "guid": "a-user-guid"
               }
            },
            "space": {
               "data": null
            },
            "organization": {
               "data": {
                  "guid": "org-guid-1"
               }
            }
         },
         "links": {
            "self": {
               "href": "http://mock.cf/v3/roles/role-guid-1"
            },
            "user": {
               "href": "http://mock.cf/v3/users/a-user-guid"
            },
            "organization": {
               "href": "http://mock.cf/v3/spaces/org-guid-1"
            }
         }
        }
      ]
    } """


@pytest.fixture()
def uaa_user_is_admin_response():
    return """
   {
      "groups": [
         {
            "value": "1234-abcd-5678-efgh-9z9d",
            "display": "cloud_controller.admin",
            "type": "DIRECT"
         }
      ]
   }"""


@pytest.fixture()
def uaa_user_is_not_admin_response():
    return """
   {
      "groups": [
         {
            "value": "1234-abcd-5678-efgh-9z9d",
            "display": "not.admin",
            "type": "DIRECT"
         }
      ]
   }"""


@pytest.fixture()
def uaa_user_has_no_groups_response():
    return """
   {
   }"""
