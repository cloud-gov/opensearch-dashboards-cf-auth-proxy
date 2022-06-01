import requests

from kibana_cf_auth_proxy.extensions import config


def get_client_credentials_token():
    response = requests.post(
        config.UAA_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": config.UAA_CLIENT_ID,
            "client_secret": config.UAA_CLIENT_SECRET,
            "response_type": "token",
        },
        auth=requests.auth.HTTPBasicAuth(
            config.UAA_CLIENT_ID, config.UAA_CLIENT_SECRET
        ),
    )

    try:
        response.raise_for_status()
    except:
        return "Unexpected error", 500

    return response.json()["access_token"]


def is_user_cf_admin(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        url = f"{config.UAA_BASE_URL}Users?attributes=groups&filter=id eq '{user_id}'"
        # there should be only one resource when filtering by ID, so no need for paginating results?
        response = s.get(url)
        try:
            response.raise_for_status()
        except:
            return "Unexpected error", 500
        data = response.json()
        all_groups = [r["groups"] for r in data["resources"]]
        group_names = [g["display"] for user_groups in all_groups for g in user_groups]
        return config.CF_ADMIN_GROUP_NAME in group_names
