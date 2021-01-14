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
