#!/usr/bin/env bash

if ! cf target > /dev/null; then
  cf api "${CF_API_URL}"
  cf auth
  cf t -o "${CF_ORGANIZATION}" -s "${CF_SPACE}"
fi

required_env_vars=(
  TEST_USER_1_USERNAME
  TEST_USER_2_USERNAME
  TEST_USER_3_USERNAME
  TEST_USER_4_USERNAME
  CF_ORG_1_NAME
  CF_ORG_2_NAME
  CF_ORG_1_SPACE_1_NAME
  CF_ORG_2_SPACE_2_NAME
  BOTH_ORGS_SPACE_NAME
)
for var in "${required_env_vars[@]}"; do
  if [ -z "${!var+x}" ]; then
    echo "$var is a required environment variable"
    exit 1
  fi
done

cf create-org "$CF_ORG_1_NAME"
cf create-org "$CF_ORG_2_NAME"

cf create-space "$CF_ORG_1_SPACE_1_NAME" -o "$CF_ORG_1_NAME"
cf create-space "$BOTH_ORGS_SPACE_NAME" -o "$CF_ORG_1_NAME"
cf create-space "$CF_ORG_2_SPACE_2_NAME" -o "$CF_ORG_2_NAME"
cf create-space "$BOTH_ORGS_SPACE_NAME" -o "$CF_ORG_2_NAME"

# User 1 is a space developer in space 1, with no org-level role
cf set-space-role "$TEST_USER_1_USERNAME" "$CF_ORG_1_NAME" "$CF_ORG_1_SPACE_1_NAME" SpaceDeveloper

# User 2 is an org manager in org 2, with no space-level role
cf set-org-role "$TEST_USER_2_USERNAME" "$CF_ORG_2_NAME" OrgManager

# User 3 is a space developer in space 1 and space 2, with no org-level roles
cf set-space-role "$TEST_USER_3_USERNAME" "$CF_ORG_1_NAME" "$CF_ORG_1_SPACE_1_NAME" SpaceDeveloper
cf set-space-role "$TEST_USER_3_USERNAME" "$CF_ORG_2_NAME" "$CF_ORG_2_SPACE_2_NAME" SpaceDeveloper

# User 4 is a space developer in space both-orgs-space in org 1, with no org-level roles
cf set-space-role "$TEST_USER_4_USERNAME" "$CF_ORG_1_NAME" "$BOTH_ORGS_SPACE_NAME" SpaceDeveloper
