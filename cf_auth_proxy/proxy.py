from flask import Response

import requests

from cf_auth_proxy.extensions import config


def proxy_request(url, headers, data, cookies, method):
    resp = requests.request(
        method=method,
        url=url,
        headers=headers,
        data=data,
        cookies=cookies,
        allow_redirects=False,
        cert=(config.DASHBOARD_CERTIFICATE, config.DASHBOARD_CERTIFICATE_KEY),
        verify=config.DASHBOARD_CERTIFICATE_CA
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    kwargs = {}
    if resp.raw.headers.get("content-encoding") == "br":
        headers.append(("content-encoding", "br"))
    if "content-type" in resp.headers:
        kwargs["content_type"] = resp.headers["content-type"]

    response = Response(resp.content, resp.status_code, headers, **kwargs)
    return response
