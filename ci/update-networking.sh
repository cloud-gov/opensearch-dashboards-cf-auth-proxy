#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit

cf api ${CF_API_URL}
cf auth 
cf t -o ${CF_ORGANIZATION} -s ${CF_SPACE}
./dev cf-network
