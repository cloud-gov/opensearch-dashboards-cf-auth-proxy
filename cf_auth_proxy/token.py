from dataclasses import dataclass
import json
from typing import Optional
import inspect

from jwcrypto.jwt import JWT, JWKSet


@dataclass(frozen=True, kw_only=True)
class Claims:
    # required per spec (https://openid.net/specs/openid-connect-core-1_0.html#IDToken)
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int

    auth_time: Optional[int] = None
    nonce: Optional[str] = None
    acr: Optional[str] = None
    amr: Optional[str] = None
    azp: Optional[str] = None

    jti: Optional[str] = None

    # ^^^ oidc-specified claims ^^^

    # vvv claims available according to http://uaa.example.com/.well-known/openid-configuration vvv
    # required because we can't do without it
    email: str
    user_id: str

    scope: Optional[str] = None
    zid: Optional[str] = None
    rev_sig: Optional[str] = None
    cid: Optional[str] = None
    user_name: Optional[str] = None
    grant_type: Optional[str] = None
    origin: Optional[str] = None
    client_id: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[str] = None

    @classmethod
    def from_dict(cls, d):
        return cls(
            **{k: v for k, v in d.items() if k in inspect.signature(cls).parameters}
        )


def decode_id_token_for_claims(id_token: str, jwks: JWKSet) -> Claims:
    """Given a JWT and a JWK set, decode the JWT and validate it"""
    token = JWT(jwt=id_token, key=jwks)
    token_claims = Claims.from_dict(json.loads(token.claims))
    return token_claims
