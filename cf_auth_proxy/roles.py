import hashlib
import requests
import logging
import json
from cf_auth_proxy.extensions import config
from typing import Optional

logger = logging.getLogger(__name__)


class RoleManager:
    def __init__(self):
        self.opensearch_url = config.OPENSEARCH_URL

    def sha256_hash(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def check_role_exists(self, role_name: str) -> bool:
        url = f"{self.opensearch_url}_plugins/_security/api/roles/{role_name}"
        response = requests.get(
            url,
            cert=(config.OPENSEARCH_CERTIFICATE, config.OPENSEARCH_CERTIFICATE_KEY),
            verify=config.OPENSEARCH_CERTIFICATE_CA,
        )
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            response.raise_for_status()

    def create_role(self, role_name: str, role_definition: dict):
        role_url = f"{self.opensearch_url}_plugins/_security/api/roles/{role_name}"
        headers = {"Content-Type": "application/json"}
        try:
            role_response = requests.put(
                role_url,
                json=role_definition,
                headers=headers,
                cert=(config.OPENSEARCH_CERTIFICATE, config.OPENSEARCH_CERTIFICATE_KEY),
                verify=config.OPENSEARCH_CERTIFICATE_CA,
            )
            if role_response.status_code not in [200, 201]:
                logger.error(
                    "failed to create role %s: %s - %s",
                    role_name,
                    role_response.status_code,
                    role_response.text,
                )
                role_response.raise_for_status()
        except Exception as e:
            logger.exception("exception in make role %s", e)
            raise

        mapping_url = (
            f"{self.opensearch_url}_plugins/_security/api/rolesmapping/{role_name}"
        )
        mapping_body = {"backend_roles": [role_name]}
        mapping_response = requests.put(
            url=mapping_url,
            json=mapping_body,
            headers=headers,
            cert=(config.OPENSEARCH_CERTIFICATE, config.OPENSEARCH_CERTIFICATE_KEY),
            verify=config.OPENSEARCH_CERTIFICATE_CA,
        )
        if mapping_response.status_code not in [200, 201]:
            logger.error(
                "failed to create backend role %s: %s - %s",
                role_name,
                mapping_response.status_code,
                mapping_response.text,
            )
            mapping_response.raise_for_status()
        return {
            "role_response": role_response.json(),
            "mapping_response": mapping_response.json(),
        }

    def build_dls(self, space_ids: list[str], org_ids: list[str]) -> Optional[dict]:
        terms_query = []
        if space_ids:
            terms_query.append({"terms": {"@cf.space_id": space_ids}})
        if org_ids:
            terms_query.append({"terms": {"@cf.org_id": org_ids}})
        if not terms_query:
            return None

        dls = {"bool": {"should": terms_query}}
        role_definition = {
            "cluster_permissions": [],
            "index_permissions": [
                {
                    "index_patterns": ["logs-app-*"],
                    "allowed_actions": ["read", "indices:monitor/settings/get"],
                    "dls": json.dumps(dls),
                }
            ],
        }
        return role_definition
