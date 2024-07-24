# Opensearch Dashboards Authentication Proxy

This is a reverse-proxy used for Cloudfoundry authentication for use with Opensearch Dashboards.

## How it works

1. When a user hits the proxy, the proxy checks if they have a valid UAA cookie.
   - If they don't, they're redirected to UAA to login.
   - If they have a UAA cookie, the proxy then:
      - Checks if it has in its cache what spaces they have access to and whether or not they're an admin.
      - If it doesn't know, it checks CAPI to find out.
2. Once the proxy has determined what spaces they're authorized for, it proxies their request to Opensearch Dashboards, setting `x-proxy-user` and `x-proxy-roles` based on whether
they're an admin or not, and setting x-proxy-ext-spaces based on their space access.

The Opensearch plugin uses x-proxy-user and x-proxy-roles to determine what role
the user has, and then uses the x-proxy-ext-spaces header to determine what
spaces the user should have access to.

## Running

The following environment variables are required:

- `FLASK_ENV` - set to `unit` for tests, `local` for development, `production` for production
- `DASHBOARD_URL` - this is the url of the proxied Opensearch dashboards instance
- `UAA_AUTH_URL` - where to send your users for authentication. Probably looks like `https://login.<domain>/oauth/authorize`
- `UAA_BASE_URL` - base URL for app where your client can exchange codes and refresh tokens for tokens. Probably looks like `https://uaa.<domain>/`.
- `UAA_CLIENT_ID` - the client ID of your uaa clinet
- `UAA_CLIENT_SECRET` - the client secret for your uaa client
- `SECRET_KEY` - the key used for cookie signing
- `DASHBOARD_CERTIFICATE` - the certificate used for signing requests to OpenSearch Dashboards
- `DASHBOARD_CERTIFICATE_KEY` - the certificate private key used for signing requests to OpenSearch Dashboards
- `DASHBOARD_CERTIFICATE_KEY` - the CA used for signing requests to OpenSearch Dashboards

The following are optional:

- `DEBUG` - whether to enable Flask's debug mode. Defaults to false
- `PORT` -  the port flask should listen on. Defaults to 8080

## Running the auth-proxy locally

1. Copy `.env-sample` to `.env` and update the configuration values
1. Run `./dev start-cluster` to start up the Docker containers for:
   - OpenSearch
   - OpenSearch Dashboards
   - A lightweight Nginx proxy (running on port `3000` by default)
1. Run `./dev serve` to start this auth-proxy (running on port `8080` by default)
   - **Note:** you must be on the VPN/using Zscaler because you will be redirected to the CF dev environment to login

### Running the e2e tests locally

After starting up the auth-proxy using the above steps, run:

```shell
./dev e2e-local
```

To debug the e2e tests (see <https://playwright.dev/python/docs/debug>):

```shell
PWDEBUG=1 ./dev e2e-local
```

You can specify [any `pytest` flags](https://docs.pytest.org/en/7.1.x/reference/reference.html#command-line-flags) or [Playwright CLI flags](https://playwright.dev/python/docs/test-runners#cli-arguments) for `e2e`.

To target specific e2e test(s):

```shell
# run the test_see_correct_logs_in_discover_user_1 test
./dev e2e-local -k 'test_see_correct_logs_in_discover_user_1'
# run all the test_see_correct_logs_in_discover_user* tests
./dev e2e-local -k 'test_see_correct_logs_in_discover_user'
```

To retain video records of failed tests:

```shell
./dev e2e-local --video retain-on-failure
```

To retain a [trace](https://playwright.dev/python/docs/trace-viewer-intro) of failed tests:

```shell
./dev e2e-local --tracing retain-on-failure
```

### Running the e2e tests against other proxy instances

Create an `.env` file for the environment you want to test. For example, to test the `dev` environment, create a `dev.env` file.

Copy the contents of `.env` to your environment specific file (e.g. `dev.env`) and update these values as necessary:

- `AUTH_PROXY_URL`
- `UAA_AUTH_URL`
- All the variables starting with `TEST_USER` with correct values for the given environment

Then, run the tests while specifying the environment you want to test as `ENVIRONMENT`:

```shell
ENVIRONMENT=dev ./dev e2e
```

### Adding client

In order to run the app locally, you will need to create a UAA client application.

First, log in to the dev jumpbox. Then, you can add create client for the app using `uaac` like so,
where `<my_url>` is the local host/port on your machine for this app (default `http://localhost:8080`):

```shell
uaac client add <my_client_name> \
   --authorized_grant_types authorization_code,refresh_token,client_credentials \
   --authorities scim.read \
   --scope "cloud_controller.read,openid,scim.read" \
   -s <my_client_secret> \
   --redirect_uri <my_url>
```

Lastly, update your `.env` value to set these values:

- `UAA_CLIENT_ID=<my_client_name>`
- `UAA_CLIENT_SECRET=<my_client_secret>`

## Downloading test results from CI

When the e2e tests run in CI, artifacts such as video recordings or traces from failed test runs may be created. To download these artifacts, use the provided script:

```shell
./scripts/download-e2e-ci-results.sh <BUILD_NUMBER>
```

`BUILD_NUMBER` should be the number of the failed `e2e` job from the pipeline.

To view downloaded trace files:

```shell
playwright show-trace ci-test-results/<dir>/trace.zip
```

where `<dir>` is an abitrary directory name generated for the test run by Playwright.

See <https://playwright.dev/python/docs/trace-viewer> for more information about working with Playwright traces.
