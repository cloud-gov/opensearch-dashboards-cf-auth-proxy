# Kibana Authentication Proxy

This is a reverse-proxy used for cf authentication for use with Open Distro for Elasticsearch.

# How it should work

(TODO: change this to "how it works" when it's done-ish)

When a user hits the proxy, the proxy checks if they have a valid UAA cookie. 
If they don't, they're redirected to UAA to login. 
If they have a UAA cookie, the proxy then checks if it has in its cache what
spaces they have access to and whether or not they're an admin. If it doesn't
know, it checks CAPI to find out. 
Once it the proxy has determined what spaces they're authorized for, it proxies their request to Kibana, setting x-proxy-user and x-proxy-roles based on whether 
they're an admin or not, and setting x-proxy-ext-spaces based on their space access.

The ODfE plugin uses x-proxy-user and x-proxy-roles to determine what role
the user has, and then uses the x-proxy-ext-spaces header to determine what
spaces the user should have access to.


# Running

The following environment variables are required:

- `FLASK_ENV` - set to `unit` for tests, `local` for development, `production` for production
- `KIBANA_URL` - this is the url of the proxied kibana instance
- `UAA_AUTH_URL` - where to send your users for authentication. Probably looks like `https://login.<domain>/oauth/authorize`
- `UAA_TOKEN_URL` - where your client can exchange codes and refresh tokens for tokens. Probably looks like `https://uaa.<domain>/token`
- `UAA_CLIENT_ID` - the client id of your uaa clinet
- `UAA_CLIENT_SECRET` - the client secret for your uaa client
- `SECRET_KEY` - the key used for cookie signing

The following are optional:

- `DEBUG` - whether to enable Flask's debug mode. Defaults to false
- `PORT` -  the port flask should listen on. Defaults to 8080


# Adding client

You can add the client for the app using `uaac` like so:

```
uaac client add <my_client_name> \
   --authorized_grant_types authorization_code,refresh_token \
   --authorities scim.read \
   --scope "cloud_controller.read,openid,scim.read" \
   -s <my_client_secret>
   --redirect-url <my_url>
```
