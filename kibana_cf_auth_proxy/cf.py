import requests

from urllib.parse import urljoin

from kibana_cf_auth_proxy.extensions import config


def iterate_cf_resource(session, first_request):
    """
    iterates over a v3-style, paginated resource, returning the full list of the resources
    """
    resources = []
    data = session.get(first_request).json()
    resources.extend(data["resources"])
    while data["pagination"]["next"] is not None:
        data = session.get(data["pagination"]["next"]["href"]).json()
        resources.extend(data["resources"])
    return resources


def get_spaces_for_user(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        url = f"{config.CF_URL}v3/roles?user_guids={user_id}&types={','.join(config.PERMITTED_SPACE_ROLES)}"
        resources = iterate_cf_resource(s, url)
    spaces = [r["relationships"]["space"]["data"]["guid"] for r in resources]
    return spaces


def get_orgs_for_user(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        url = f"{config.CF_URL}v3/roles?user_guids={user_id}&types={','.join(config.PERMITTED_ORG_ROLES)}"
        resources = iterate_cf_resource(s, url)
    orgs = [r["relationships"]["organization"]["data"]["guid"] for r in resources]
    return orgs
