#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit || true

function cleanup() {
  [[ -n "${ssh_pid:-}" ]] && kill "${ssh_pid}"
}
trap cleanup exit

cf api "${CF_API_URL}"
cf auth
cf t -o "${CF_ORGANIZATION}" -s "${CF_SPACE}"

echo "Creating SSH tunnel"
cf ssh -L 9200:opensearch-test.apps.internal:9200 -L 5601:dashboard-test.apps.internal:5601 "${DASHBOARDS_APP_NAME}" -N &
ssh_pid=$!

echo "Waiting for tunnel to come up ..."
sleep 10

./dev seed-es-data
