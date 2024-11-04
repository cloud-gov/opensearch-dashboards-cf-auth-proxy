from urllib.parse import urljoin
import requests

from cf_auth_proxy.extensions import config


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
        timeout=config.REQUEST_TIMEOUT,
    )

    try:
        response.raise_for_status()
    except:
        return "Unexpected error", 500

    return response.json()["access_token"]


def is_user_cf_admin(user_id, token):
    with requests.Session() as s:
        s.headers["Authorization"] = f"Bearer {token}"
        url = urljoin(config.UAA_BASE_URL, f"Users/{user_id}")
        response = s.get(url)
        response.raise_for_status()
        data = response.json()
        user_groups = [group["display"] for group in data.get("groups", [])]
        return config.CF_ADMIN_GROUP_NAME in user_groups
