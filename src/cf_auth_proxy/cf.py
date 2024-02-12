from urllib.parse import urljoin
import requests

from opensearch_dashboards_cf_auth_proxy.extensions import config


def iterate_cf_resource(session, first_response):
    """
    iterates over a v3-style, paginated resource, returning the full list of the resources
    """
    resources = []
    data = first_response.json()
    resources.extend(data["resources"])
    while data["pagination"]["next"] is not None:
        data = session.get(data["pagination"]["next"]["href"]).json()
        resources.extend(data["resources"])
    return resources


def get_spaces_for_user(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        params = {
            "user_guids": user_id,
            "types": ",".join(config.PERMITTED_SPACE_ROLES),
        }
        url = urljoin(config.CF_API_URL, "v3/roles")
        first_response = s.get(url, params=params)
        resources = iterate_cf_resource(s, first_response)
    spaces = [r["relationships"]["space"]["data"]["guid"] for r in resources]
    return spaces


def get_orgs_for_user(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        params = {"user_guids": user_id, "types": ",".join(config.PERMITTED_ORG_ROLES)}
        url = urljoin(config.CF_API_URL, "v3/roles")
        first_response = s.get(url, params=params)
        resources = iterate_cf_resource(s, first_response)
    orgs = [r["relationships"]["organization"]["data"]["guid"] for r in resources]
    return orgs
