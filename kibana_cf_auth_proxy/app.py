from base64 import b64encode, b64decode, urlsafe_b64encode, urlsafe_b64decode
import urllib.parse
import os

from flask import Flask, request, session, url_for, redirect
from flask_session import Session

from kibana_cf_auth_proxy.extensions import config
from kibana_cf_auth_proxy.proxy import proxy_request


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    Session(app)

    @app.route("/ping")
    def ping():
        return "PONG"

    @app.route("/cb")
    def callback():
        pass

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def handle_request(path):
        def redirect_to_auth():
            session["state"] = urlsafe_b64encode(os.urandom(24)).decode('utf-8')
            params = {
                "state": session["state"],
                "client_id": config.UAA_CLIENT_ID,
                "response_type": "code",
                "scope": "openid email",
                "redirect_uri": url_for("callback", _external=True)
            }
            params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{config.UAA_AUTH_URL}?{params}"
            return redirect(url)

        if session.get("user") is None:
            return redirect_to_auth()
        forbidden_headers = {"host", "x-proxy-user", "x-proxy-ext-spaces"}
        url = request.url.replace(request.host_url, config.KIBANA_URL)
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in forbidden_headers
        }

        return proxy_request(
            url, headers, request.get_data(), request.cookies, request.method
        )

    return app
