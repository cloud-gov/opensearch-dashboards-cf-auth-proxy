import hashlib
import requests
import json
from cf_auth_proxy.extensions import config

class RoleManager:
    def __init__(self,session,opensearch_url):
        self.session = session
        self.opensearch_url = config.OPENSEARCH_URL

    def sha256_hash(self,value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def check_role_exists(self,role_name) -> bool:
        url = f'{self.opensearch_url}/_plugins/_security/api/roles/{role_name}'
        response = requests.get(
            url,
            cert=(config.OPENSEARCH_CERTIFICATE, config.OPENSEARCH_CERTIFICATE_KEY),
            verify=config.OPENSEARCH_CERTIFICATE_CA
        )
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            response.raise_for_status()

    def create_role(self,role_name: str, role_definition:dict):
        url = f"{self.opensearch_url}/_plugins/_security/api/roles/{role_name}"
        response = requests.put(
            url,
            json=role_definition,
            cert=(config.OPENSEARCH_CERTIFICATE, config.OPENSEARCH_CERTIFICATE_KEY),
            verify=config.OPENSEARCH_CERTIFICATE_CA
        )
        if response.status_code not in [200,201]:
            response.raise_for_status()
        return response.json()

    def build_dls(space_ids,org_ids):
        terms_query = []

        if space_ids:
            terms_query.append({"terms": {"@cf.space_id": space_ids}})
        if org_ids:
            terms_query.append({"terms": {"@cf.org_ids": org_ids}})
        if not terms_query:
            return None

        dls = {"bool": {"should": terms_query}}
        role_definition = {
            "cluster_permissions": [],
            "index_permissions": [
                {
                    "index_patterns": ["logs-app-*"],
                    "allowed_actions": ["read","indices:monitor/settings/get"],
                    "dls": json.dumps(dls)
                }
                ]
        }
        return role_definition

