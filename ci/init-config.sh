#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit || true
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function cleanup() {
  [[ -n "${ssh_pid:-}" ]] && kill "${ssh_pid}"
}
trap cleanup exit

cf api "${CF_API_URL}"
cf auth
cf t -o "${CF_ORGANIZATION}" -s "${CF_SPACE}"

echo "Creating SSH tunnel"
cf ssh -L 9200:opensearch-test.apps.internal:9200 -L 5601:kbn-test.apps.internal:5601 kibana -N &
ssh_pid=$!

echo "Waiting for tunnel to come up ..."
sleep 10

bash "${dir}/seed-es-data.sh"
