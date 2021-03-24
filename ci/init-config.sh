#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit


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

cookie_jar=$(mktemp)

echo "Waiting for tunnel to come up ..."
sleep 10

# we have to create index and component templates
# to work around the baked-in stream templates
echo "creating component template"
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X PUT \
    -H "content-type: application/json" \
    https://localhost:9200/_component_template/ct_apps \
    -d '{
    "template": {
        "settings": {
            "number_of_shards": 1
        },
        "mappings": {
            "properties": {
                "@cf": {
                    "type": "object",
                    "dynamic": true,
                    "properties": {
                        "space_id": {
                            "type": "keyword",
                            "index": true
                        },
                        "org_id": {
                            "type": "keyword",
                            "index": true
                        }
                    }
                }
            }
        }
    }
}' | jq

echo "Creating index template"
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X PUT \
    -H "content-type: application/json" \
    https://localhost:9200/_index_template/it_apps \
    -d '{
         "index_patterns" : ["logs-app-*"],
          "priority" : 1,
          "composed_of": ["ct_apps"]
        }' | jq

echo "Creating index"
curl --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X PUT \
    https://localhost:9200/logs-app-now \
    -d '{
    "mappings": {
        "properties": {
            "@cf": {
                "type": "object",
                "dynamic": true,
                "properties": {
                    "@cf": {
                        "space_id": {
                            "type": "keyword",
                            "index": true
                        },
                        "org_id": {
                            "type": "keyword",
                            "index": true
                        }
                    }
                }
            }
        }
    }
}' | jq


# next we add some logs
# the idea is to add one log for each test
#  - user should be able to see logs with their space id
#  - user should not be able to see logs with the wrong space id
#  - user should not be able to see logs without a space id

# We should have this set up ahead of time:
#   - org 1 has space space 1 with id ${CF_SPACE_ID_1}
#   - org 2 has space space 2 with id ${CF_SPACE_ID_2}
#   - user 1 is a space developer in space 1, with no org-level role
#   - user 2 is an org manager in org 2, with no space-level role
#   - user 3 is a space developer in space 1 and space 2, with no org-level roles

# we're using features from `date` that the default MacOS date
# doesn't have installed, so we need to figure out what `date`
# to use
date_bin=date

if [[ ! $(${date_bin} --iso-8601 2> /dev/null) ]]; then
    if [[ $(which gdate) ]]; then
        date_bin=gdate
    else
        echo "Can't find a suitable date program"
        echo "try \`brew install coreutils\` if you're on MacOS"
        exit 1
    fi
fi

time=$(${date_bin} --iso-8601=seconds)

# user 1 should be able to see this log
# user 2 should not be able to see it
# user 3 should be able to see this log
echo "creating test document 1/5"
# we use refresh=true on all these to force elasticsearch to refresh
# It doesn't seem to make the docs available otherwise
# We could probably just do this on the last doc we index, but doing
# it on all of them makes it easier to modify the script
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {
            "space_id":"'${CF_SPACE_ID_1}'"
        },
        "message": "space_id_1"
        }' | jq

# user 1 should not be able to see it
# user 2 should be able to see this log
# user 3 should be able to see this log
echo "creating test document 2/5"
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {
            "space_id":"'${CF_SPACE_ID_2}'"
        },
        "message": "space_id_2"
        }' | jq

# none of the users should be able to see this log
echo "creating test document 3/5"
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "message": "no_space_id"
        }' | jq

# user 1 should be able to see this log
# user 2 should not be able to see it
# user 3 should be able to see this log
echo "creating test document 4/5"
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf":{ "org_id":"'${CF_ORG_ID_1}'"},
        "message": "org_id_1"
        }' | jq

# user 1 should not be able to see it
# user 2 should be able to see this log
# user 3 should be able to see this log
echo "creating test document 5/5"
curl --fail --silent --show-error -u ${ES_USER}:${ES_PASSWORD} -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {"org_id":"'${CF_ORG_ID_2}'"},
        "message": "org_id_2"
        }' | jq

# for the kibana stuff, we need cookies just to deal with the multitenancy
echo "Setting up kibana http session"
# this curl is just to get a cookie ready 
curl --fail --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X GET \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "kbn-xsrf: 1" \
    -H "kbn-version: 7.10.0" \
    http://localhost:5601/api/v1/configuration/account | jq

echo "Switching to default tenant"
curl --fail --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X POST \
    -H "content-type: application/json" \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "kbn-version: 7.10.0" \
    http://localhost:5601/api/v1/multitenancy/tenant \
    -d '{"tenant":"","username":"'${ES_USER}'"}'

echo "Creating index pattern"
curl --fail --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X POST \
    -H "content-type: application/json" \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "kbn-version: 7.10.0" \
    http://localhost:5601/api/saved_objects/index-pattern \
    -d '
    {
  "attributes": {
    "title": "logs-app-*",
    "timeFieldName": "@timestamp"
    }
    }' | jq

echo "Setting default index"
curl --fail --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X POST \
    -H "content-type: application/json" \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "kbn-version: 7.10.0" \
    http://localhost:5601/api/kibana/settings \
    -d '{"changes":{"defaultIndex":"logs-app-*"}}' | jq
