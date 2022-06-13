#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit || true


function cleanup() {
  [[ -n "${ssh_pid:-}" ]] && kill ${ssh_pid}
  rm ${cookie_jar}
}
trap cleanup exit

cf api ${CF_API_URL}
cf auth
cf t -o ${CF_ORGANIZATION} -s ${CF_SPACE}

echo "Creating SSH tunnel"
cf ssh -L 9200:odfe-test.apps.internal:9200 -L 5601:kbn-test.apps.internal:5601 kibana -N &
ssh_pid=$!

echo "Waiting for tunnel to come up ..."
sleep 10

./seed-es-data.sh