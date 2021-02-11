These manifests are for a Cloud Foundry-based cluster with 1 elasticsearch,
1 redis, and 1 auth-proxy instance.

These are separate manifests because the concourse cf resource doesn't
work with multiple apps in a manifest.

# SECURITY NOTICE
This cluster is totally insecure and non-durable. It should only be used
for testing the proxy and should NEVER have any sensitive or important data.
