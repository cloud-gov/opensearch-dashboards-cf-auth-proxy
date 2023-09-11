#!/usr/bin/env bash

if ! cf target > /dev/null; then
  cf api "${CF_API_URL}"
  cf auth
  cf t -o "${CF_ORGANIZATION}" -s "${CF_SPACE}"
fi

if [[ -z "$TEST_USER_1_USERNAME" ]]; then
  echo "TEST_USER_1_USERNAME environment variable is required"
  exit 1
fi

if [[ -z "$TEST_USER_2_USERNAME" ]]; then
  echo "TEST_USER_2_USERNAME environment variable is required"
  exit 1
fi

if [[ -z "$TEST_USER_3_USERNAME" ]]; then
  echo "TEST_USER_3_USERNAME environment variable is required"
  exit 1
fi

if [[ -z "$TEST_USER_4_USERNAME" ]]; then
  echo "TEST_USER_4_USERNAME environment variable is required"
  exit 1
fi

ORG_1="kibana-test-org-1"
ORG_2="kibana-test-org-2"

ORG_1_SPACE_1="test-kibana-space-1"
ORG_2_SPACE_2="test-kibana-space-2"
BOTH_ORGS_SPACE="both-orgs-space"

cf create-org "$ORG_1"
cf create-org "$ORG_2"

cf create-space "$ORG_1_SPACE_1" -o "$ORG_1"
cf create-space "$BOTH_ORGS_SPACE" -o "$ORG_1"
cf create-space "$ORG_2_SPACE_2" -o "$ORG_2"
cf create-space "$BOTH_ORGS_SPACE" -o "$ORG_2"

# User 1 is a space developer in space 1, with no org-level role
cf set-space-role "$TEST_USER_1_USERNAME" "$ORG_1" "$ORG_1_SPACE_1" SpaceDeveloper

# User 2 is an org manager in org 2, with no space-level role
cf set-org-role "$TEST_USER_2_USERNAME" "$ORG_2" OrgManager

# User 3 is a space developer in space 1 and space 2, with no org-level roles
cf set-space-role "$TEST_USER_3_USERNAME" "$ORG_1" "$ORG_1_SPACE_1" SpaceDeveloper
cf set-space-role "$TEST_USER_3_USERNAME" "$ORG_2" "$ORG_2_SPACE_2" SpaceDeveloper

# User 4 is a space developer in space both-orgs-space in org 1, with no org-level roles
cf set-space-role "$TEST_USER_4_USERNAME" "$ORG_1" "$BOTH_ORGS_SPACE" SpaceDeveloper
