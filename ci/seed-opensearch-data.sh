#!/usr/bin/env bash

set -euo pipefail
shopt -s inherit_errexit 2>/dev/null || true

function cleanup() {
  rm "${cookie_jar}"
}
trap cleanup exit

cookie_jar=$(mktemp)

required_env_vars=(
    OPENSEARCH_USER
    OPENSEARCH_PASSWORD
    CF_ORG_1_ID
    CF_ORG_1_SPACE_1_ID
    CF_ORG_1_BOTH_ORGS_SPACE_ID
    CF_ORG_2_ID
    CF_ORG_2_SPACE_2_ID
    CF_ORG_2_BOTH_ORGS_SPACE_ID
)
for var in "${required_env_vars[@]}"; do
    if [ -z "${!var+x}" ]; then
        echo "$var is a required environment variable"
        exit 1
    fi
done

function curl_and_handle_output() {
    handle_response=$1
    shift
    OUTPUT_FILE=$(mktemp)
    HTTP_CODE=$(curl --silent \
        --output "$OUTPUT_FILE" \
        --write-out "%{http_code}" \
        "$@")
    if $handle_response "$HTTP_CODE"; then
        cat "$OUTPUT_FILE"
        rm "$OUTPUT_FILE"
    else
        >&2 echo "failing HTTP code: $HTTP_CODE"
        cat "$OUTPUT_FILE"
        rm "$OUTPUT_FILE"
        exit 22
    fi
}

function accept_200_404_response() {
    if [[ $1 != "200" && $1 != "404" ]]; then
        return 1
    fi
    return 0
}

function accept_200_response() {
    if [[ $1 != "200" ]]; then
        return 1
    fi
    return 0
}

# we have to create index and component templates
# to work around the baked-in stream templates
echo "creating component template"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
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
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X PUT \
    -H "content-type: application/json" \
    https://localhost:9200/_index_template/it_apps \
    -d '{
         "index_patterns" : ["logs-app-*"],
          "priority" : 1,
          "composed_of": ["ct_apps"]
        }' | jq

# Delete index if it already exists
echo "Deleting index (if it already exists)"
curl_and_handle_output accept_200_404_response -k \
    -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" \
    -X DELETE \
    https://localhost:9200/logs-app-now | jq

echo "Creating index"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X PUT \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now \
    -d '{
    "mappings": {
        "properties": {
            "@cf": {
                "dynamic": true,
                "type": "object",
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
}' | jq


# next we add some logs
# the idea is to add one log for each test
#  - user should be able to see logs with their space id
#  - user should not be able to see logs with the wrong space id
#  - user should not be able to see logs without a space id

# We should have this set up ahead of time:
#   - org 1 has space space 1 with id ${CF_ORG_1_SPACE_1_ID}
#   - org 2 has space space 2 with id ${CF_ORG_2_SPACE_2_ID}
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
# user 4 should not be able to see it
echo "creating test document 1/7"
# we use refresh=true on all these to opensearch to refresh
# It doesn't seem to make the docs available otherwise
# We could probably just do this on the last doc we index, but doing
# it on all of them makes it easier to modify the script
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {
            "org_id": "'${CF_ORG_1_ID}'",
            "space_id":"'${CF_ORG_1_SPACE_1_ID}'"
        },
        "message": "space_id_1"
        }' | jq

# user 1 should not be able to see it
# user 2 should be able to see this log
# user 3 should be able to see this log
# user 4 should not be able to see it
echo "creating test document 2/7"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {
            "org_id": "'${CF_ORG_2_ID}'",
            "space_id":"'${CF_ORG_2_SPACE_2_ID}'"
        },
        "message": "space_id_2"
        }' | jq

# none of the users should be able to see this log
echo "creating test document 3/7"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "message": "no_space_id"
        }' | jq

# user 1 should not be able to see this log
# user 2 should not be able to see it
# user 3 should be able to see this log
# user 4 should not be able to see it
echo "creating test document 4/7"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf":{ "org_id":"'${CF_ORG_1_ID}'"},
        "message": "org_id_1"
        }' | jq

# user 1 should not be able to see it
# user 2 should be able to see this log
# user 3 should be able to see this log
# user 4 should not be able to see it
echo "creating test document 5/7"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {"org_id":"'${CF_ORG_2_ID}'"},
        "message": "org_id_2"
        }' | jq

# user 1 should not be able to see it
# user 2 should not be able to see it
# user 3 should not be able to see it
# user 4 should be able to see this log
echo "creating test document 6/7"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {
            "org_id": "'${CF_ORG_1_ID}'",
            "space_id":"'${CF_ORG_1_BOTH_ORGS_SPACE_ID}'"
        },
        "message": "org_1_both_orgs_space"
        }' | jq

# user 1 should not be able to see it
# user 2 should be able to see this log
# user 3 should not be able to see it
# user 4 should not be able to see it
echo "creating test document 7/7"
curl --fail-with-body --silent --show-error -u "${OPENSEARCH_USER}":"${OPENSEARCH_PASSWORD}" -k \
    -X POST \
    -H "content-type: application/json" \
    https://localhost:9200/logs-app-now/_doc?refresh=true \
    -d '{
        "@timestamp": "'${time}'",
        "@cf": {
            "org_id": "'${CF_ORG_2_ID}'",
            "space_id":"'${CF_ORG_2_BOTH_ORGS_SPACE_ID}'"
        },
        "message": "org_2_both_orgs_space"
        }' | jq

# for the opensearch dashboards stuff, we need cookies just to deal with the multitenancy
echo "Setting up opensearch dashboards http session"
# this curl is just to get a cookie ready
curl --fail-with-body --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X GET \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "osd-xsrf: true" \
    http://localhost:5601/api/v1/configuration/account | jq

echo "Switching to default tenant"
curl --fail-with-body --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X POST \
    -H "content-type: application/json" \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "osd-xsrf: true" \
    http://localhost:5601/api/v1/multitenancy/tenant \
    -d '{"tenant":"","username":"'"${OPENSEARCH_USER}"'"}'


echo "Creating index pattern"
OUTPUT=$(curl_and_handle_output accept_200_response \
    --cookie-jar "${cookie_jar}" -b "${cookie_jar}" \
    -X POST \
    -H "content-type: application/json" \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "osd-xsrf: true" \
    -d '
    {
        "attributes": {
            "title": "logs-app-*",
            "timeFieldName": "@timestamp"
        }
    }' \
    http://localhost:5601/api/saved_objects/index-pattern)
echo "$OUTPUT" | jq
INDEX_PATTERN_GUID=$(echo "$OUTPUT" | jq -r '.id')

echo "Setting default index"
curl --fail-with-body --silent --show-error --cookie-jar ${cookie_jar} -b ${cookie_jar} \
    -X POST \
    -H "content-type: application/json" \
    -H "x-proxy-roles: admin" \
    -H "x-proxy-user: admin" \
    -H 'x-forwarded-for: 127.0.0.1' \
    -H "osd-xsrf: true" \
    http://localhost:5601/api/opensearch-dashboards/settings \
    -d "{\"changes\":{\"defaultIndex\":\"$INDEX_PATTERN_GUID\"}}" | jq
