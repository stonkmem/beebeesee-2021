from pathlib import Path
from flask import Flask
from .info import (
    PROJECT_NAME,
    ROOT_DIR,
    STATIC_DIR,
    VIEWS_DIR,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_DEBUG,
)
from .site import site

app = Flask(PROJECT_NAME, static_url_path="", static_folder=STATIC_DIR)
app.register_blueprint(site)


def main(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=DEFAULT_DEBUG):
    print(f"{ROOT_DIR=}")
    print(f"{STATIC_DIR=}")
    print(f"{VIEWS_DIR=}")
    app.run(
        host=host,
        port=port,
        debug=debug,
        ssl_context=(ROOT_DIR / "cert.pem", ROOT_DIR / "key.pem")
    )
