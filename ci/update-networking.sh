#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

pushd ${dir}
trap popd exit

cf api ${CF_API_URL}
cf auth
cf t -o ${CF_ORGANIZATION} -s ${CF_SPACE}

sleep 10

../dev cf-network "$OPENSEARCH_MANAGER_APP_NAME" "$OPENSEARCH_NODE_APP_NAME" "$DASHBOARDS_APP_NAME" "$PROXY_APP_NAME"
