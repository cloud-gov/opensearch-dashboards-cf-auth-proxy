from flask import Flask, request


from kibana_cf_auth_proxy.extensions import config
from kibana_cf_auth_proxy.proxy import proxy_request


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)

    @app.route("/ping")
    def ping():
        return "PONG"

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def handle_request(path):
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
