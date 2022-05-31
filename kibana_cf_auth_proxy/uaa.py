import requests

from kibana_cf_auth_proxy.extensions import config


def iterate_user_resources(session, first_url):
    """
    iterates over paginated resources of user info, returning the full list of the resources
    """
    resources = []
    data = session.get(first_url).json()
    resources.extend(data["resources"])
    # this logic is wrong
    while data["startIndex"] < data['totalResults']:
        newStartIndex = data["startIndex"] + data["itemsPerPage"]
        itemsPerPage = data["itemsPerPage"]
        data = session.get(f"{first_url}&startIndex={newStartIndex}&itemsPerPage={itemsPerPage}").json()
        resources.extend(data["resources"])
    return resources


def get_user_groups(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        url = f"{config.UAA_BASE_URL}Users?attributes=groups&filter=id eq '{user_id}'"
        # there should be only one resource when filtering by ID, so no need for paginating results?
        data = s.get(url).json()
        all_groups = [r["groups"] for r in data["resources"]]
        group_names = [g["display"] for user_groups in all_groups for g in user_groups]
        return group_names