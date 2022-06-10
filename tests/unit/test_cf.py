import pytest
import requests_mock

from kibana_cf_auth_proxy import cf


def test_gets_spaces():
    with requests_mock.Mocker() as m:
        response_1 = """
  {
   "pagination": {
      "total_results": 2,
      "total_pages": 2,
      "first": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=space_developer%2Cspace_manager&user_guids=a-user-guid"
      },
      "last": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=space_developer%2Cspace_manager%2Cspace_auditor&user_guids=a-user-guid"
      },
      "next": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=space_developer%2Cspace_manager%2Cspace_auditor&user_guids=a-user-guid"
      },
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
        response_2 = """
  {
   "pagination": {
      "total_results": 2,
      "total_pages": 2,
      "first": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=space_developer%2Cspace_manager%2Cspace_auditor&user_guids=a-user-guid"
      },
      "last": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=space_developer%2Cspace_manager%2Cspace_auditor&user_guids=a-user-guid"
      },
      "next": null,
      "previous": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=space_developer%2Cspace_manager%2Cspace_auditor&user_guids=a-user-guid"
      }
   },
   "resources": [
      {
         "guid": "role-guid-2",
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
                  "guid": "space-guid-2"
               }
            },
            "organization": {
               "data": null
            }
         },
         "links": {
            "self": {
               "href": "http://mock.cf/v3/roles/role-guid-2"
            },
            "user": {
               "href": "http://mock.cf/v3/users/a-user-guid"
            },
            "space": {
               "href": "http://mock.cf/v3/spaces/space-guid-2"
            }
         }
        }
      ]
    }
    """
        m.get(
            "http://mock.cf/v3/roles?user_guids=a-user-id&types=space_developer,space_manager,space_auditor",
            text=response_1,
        )
        m.get(
            "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=space_developer%2Cspace_manager%2Cspace_auditor&user_guids=a-user-guid",
            text=response_2,
        )
        assert sorted(cf.get_spaces_for_user("a-user-id", "a_token")) == sorted(
            ["space-guid-1", "space-guid-2"]
        )


def test_gets_roles():
    with requests_mock.Mocker() as m:
        response_1 = """
  {
   "pagination": {
      "total_results": 2,
      "total_pages": 2,
      "first": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=organization_manager%2Corganization_auditor&user_guids=a-user-guid"
      },
      "last": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=organization_manager%2Corganization_auditor&user_guids=a-user-guid"
      },
      "next": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=organization_manager%2Corganization_auditor&user_guids=a-user-guid"
      },
      "previous": null
   },
   "resources": [
      {
         "guid": "role-guid-1",
         "created_at": "2019-12-12T18:59:12Z",
         "updated_at": "2019-12-12T18:59:13Z",
         "type": "org_manager",
         "relationships": {
            "user": {
               "data": {
                  "guid": "a-user-guid"
               }
            },
            "organization": {
               "data": {
                  "guid": "org-guid-1"
               }
            },
            "space": {
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
            "organization": {
               "href": "http://mock.cf/v3/organization/org-guid-1"
            }
         }
        }
      ]
    } """
        response_2 = """
  {
   "pagination": {
      "total_results": 2,
      "total_pages": 2,
      "first": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=organization_manager,organization_auditor&user_guids=a-user-guid"
      },
      "last": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=organization_manager,organization_auditor&user_guids=a-user-guid"
      },
      "next": null,
      "previous": {
         "href": "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=1&per_page=1&types=organization_manager,organization_auditor&user_guids=a-user-guid"
      }
   },
   "resources": [
      {
         "guid": "role-guid-2",
         "created_at": "2019-12-12T18:59:12Z",
         "updated_at": "2019-12-12T18:59:13Z",
         "type": "org_manager",
         "relationships": {
            "user": {
               "data": {
                  "guid": "a-user-guid"
               }
            },
            "organization": {
               "data": {
                  "guid": "org-guid-2"
               }
            },
            "space": {
               "data": null
            }
         },
         "links": {
            "self": {
               "href": "http://mock.cf/v3/roles/role-guid-2"
            },
            "user": {
               "href": "http://mock.cf/v3/users/a-user-guid"
            },
            "organization": {
               "href": "http://mock.cf/v3/organizations/org-guid-2"
            }
         }
        }
      ]
    }
    """
        m.get(
            "http://mock.cf/v3/roles?user_guids=a-user-id&types=organization_manager,organization_auditor",
            text=response_1,
        )
        m.get(
            "http://mock.cf/v3/roles?order_by=%2Bcreated_at&page=2&per_page=1&types=organization_manager,organization_auditor&user_guids=a-user-guid",
            text=response_2,
        )
        assert sorted(cf.get_orgs_for_user("a-user-id", "a_token")) == sorted(
            ["org-guid-1", "org-guid-2"]
        )
