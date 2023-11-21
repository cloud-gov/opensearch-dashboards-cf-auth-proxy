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

The following are optional:

- `DEBUG` - whether to enable Flask's debug mode. Defaults to false
- `PORT` -  the port flask should listen on. Defaults to 8080

## Running the auth-proxy locally

1. Copy `.env-sample` to `.env` and update the configuration values
1. From the `docker` directory, run `docker-compose up`
1. Run `./dev serve` (note: you must be on the VPN/using Zscaler because you will be redirected to the CF dev environment to login)

### Running the e2e tests locally

After starting up the auth-proxy using the above steps, run:

```shell
./dev e2e-local
```

To debug the e2e tests (see <https://playwright.dev/python/docs/debug>):

```shell
PWDEBUG=1 ./dev e2e-local
```

To target specific e2e test(s), you can supply an `E2E_TEST_FILTER` environment variable:

```shell
E2E_TEST_FILTER="discover_user" ./dev e2e-local
```

To retain video records of failed tests:

```shell
./dev e2e-local --video retain-on-failure
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
