#!/usr/bin/env bash

# Login to UAA
uaac target "$UAA_API_URL"
uaac token client get "$UAA_CLIENT_ID" -s "$UAA_CLIENT_SECRET"

TEST_USER_CREDENTIAL_NAMES=$(echo "$TEST_USERS_CREDENTIAL_USERNAME_MAP" | jq '. | keys | join(" ")')

for credential_name in $TEST_USER_CREDENTIAL_NAMES; do
  echo "updating password credential for $credential_name"

  # Generate a new password for the credential
  credhub regenerate -n "/concourse/main/opensearch-dashboards-cf-auth-proxy/$credential_name"

  # Get the UAA username for the corresponding Credhub credential
  USERNAME=$(echo "$CREDENTIAL_USERNAME_MAP" | jq --arg credential_name "$credential_name" '.[$credential_name]')

  echo "updating UAA password for $USERNAME"

  # Get the new password from Credhub
  PASSWORD=$(credhub get -n "/concourse/main/opensearch-dashboards-cf-auth-proxy/$credential_name" --output-json | jq -r '.value')

  # Update the user password in UAA with the new value from Credhub
  uaac password set "$USERNAME" --password "$PASSWORD"

  # Activate the user, just to be safe
  uaac user activate "$USERNAME"
done



