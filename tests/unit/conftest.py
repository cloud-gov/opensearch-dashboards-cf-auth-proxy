import json

from jwcrypto import jwk
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat

import pytest


key_type = "RSA"
alg = "RSA256"
use = "sig"

def make_key(name):
    return jwk.JWK.generate(kty=key_type, size=2048, kid=name, use=use, alg=alg)

@pytest.fixture(scope='session')
def rsa_keypair_0():
    rsa_key = make_key("key-0")
    return rsa_key


@pytest.fixture(scope='session')
def rsa_keypair_1():
    rsa_key = make_key("key-1")
    return rsa_key


@pytest.fixture
def token_keys(rsa_keypair_0, rsa_keypair_1) -> str:
    keyset = jwk.JWKSet()
    keyset.add(rsa_keypair_0)
    keyset.add(rsa_keypair_1)
    export = keyset.export(private_keys=False)
    return export
