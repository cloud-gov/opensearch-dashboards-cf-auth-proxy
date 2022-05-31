import requests

from kibana_cf_auth_proxy.extensions import config

def get_user_groups(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        url = f"{config.UAA_BASE_URL}Users?attributes=groups&filter=id eq '{user_id}'"
        # there should be only one resource when filtering by ID, so no need for paginating results?
        data = s.get(url).json()
        all_groups = [r["groups"] for r in data["resources"]]
        group_names = [g["display"] for user_groups in all_groups for g in user_groups]
        return group_names