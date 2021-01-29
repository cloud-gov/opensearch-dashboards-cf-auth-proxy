from base64 import b64encode, b64decode, urlsafe_b64encode, urlsafe_b64decode
import urllib.parse
import os
import datetime

from flask import Flask, request, session, url_for, redirect
from flask_session import Session
import jwt
import requests

from kibana_cf_auth_proxy.extensions import config
from kibana_cf_auth_proxy.proxy import proxy_request
from kibana_cf_auth_proxy import cf


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    Session(app)

    @app.before_request
    def refresh_session():
        access_token_expiration = session.get("access_token_expiration")
        if access_token_expiration is not None:
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            if now_utc.timestamp() - access_token_expiration <= 30:
                r = requests.post(
                    config.UAA_TOKEN_URL,
                    data={
                        "client_id": config.UAA_CLIENT_ID,
                        "client_secret": config.UAA_CLIENT_SECRET,
                        "grant_type": "refresh_token",
                        "token_format": "opaque",
                        "refresh_token": session["refresh_token"],
                    },
                )
                try:
                    r.raise_for_status()
                except:
                    # nuke the session.
                    # this prevents looping failure, and also fails closed
                    # in case the problem is that the user is not authorized
                    for key in session:
                        session.pop(key)
                    # TODO: improve this with logging and a branded, friendly error page
                    return "Unexpected error", 500
                data = r.json()
                session["access_token"] = data["access_token"]
                session["refresh_token"] = data["refresh_token"]
                expiration = now_utc + datetime.timedelta(seconds=data["expires_in"])
                session["access_token_expiration"] = expiration.timestamp()

    @app.route("/ping")
    def ping():
        print(session.modified)
        return "PONG"

    @app.route("/cb")
    def callback():
        # TODO: what do we do with errors passed back from the authn server?
        code = request.args["code"]

        req_csrf = request.args.get("state")
        # pop to invalidate the CSRF
        sess_csrf = session.pop("state")

        if sess_csrf != req_csrf:
            # TODO: make a view for this
            return "bad request", 403

        # stash now before we get our token, to give ourselves the edge on timing issues
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        r = requests.post(
            config.UAA_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": url_for("callback", _external=True),
            },
            auth=requests.auth.HTTPBasicAuth(
                config.UAA_CLIENT_ID, config.UAA_CLIENT_SECRET
            ),
        )
        try:
            r.raise_for_status()
        except:
            return "Unexpected error", 500

        response = r.json()

        # TODO: validate jwt token
        token = jwt.decode(
            response.get("id_token"), algorithms=["RS256", "ES256"],options=dict(verify_signature=False)
        )

        session["user_id"] = token["user_id"]
        session["access_token"] = response["access_token"]
        session["refresh_token"] = response["refresh_token"]
        expiration = now_utc + datetime.timedelta(seconds=response["expires_in"])
        session["access_token_expiration"] = expiration.timestamp()
        session["id_token"] = response["id_token"]
        session["spaces"] = cf.get_spaces_for_user(
            session["user_id"], session["access_token"]
        )
        session["orgs"] = cf.get_orgs_for_user(
            session["user_id"], session["access_token"]
        )
        return "logged in"

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def handle_request(path):
        def redirect_to_auth():
            session["state"] = urlsafe_b64encode(os.urandom(24)).decode("utf-8")
            params = {
                "state": session["state"],
                "client_id": config.UAA_CLIENT_ID,
                "response_type": "code",
                "scope": "openid cloud_controller.read scim.read",
                "redirect_uri": url_for("callback", _external=True),
            }
            params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{config.UAA_AUTH_URL}?{params}"
            return redirect(url)

        if session.get("user_id") is None:
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
