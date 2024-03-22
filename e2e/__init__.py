from os import getenv
import sys

AUTH_PROXY_URL = getenv("AUTH_PROXY_URL")
if AUTH_PROXY_URL is None:
    print("AUTH_PROXY_URL is a required environment variable, exiting")
    sys.exit(1)

UAA_AUTH_URL = getenv("UAA_AUTH_URL")
if UAA_AUTH_URL is None:
    print("UAA_AUTH_URL is a required environment variable, exiting")
    sys.exit(1)
