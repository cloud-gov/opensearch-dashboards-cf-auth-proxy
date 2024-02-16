#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit

src/dev set-up-environment
src/venv/bin/bandit -r src/src/cf_auth_proxy
src/dev test
