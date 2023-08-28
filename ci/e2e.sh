#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit

apt-get update
apt-get install -y python3-venv

src/dev set-up-ci-environment
src/dev e2e --video retain-on-failure
