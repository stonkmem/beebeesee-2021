import subprocess as sp
from typing import *
from .info import DEFAULT_PORT, DEFAULT_HOST

ENVIRONMENT_VARIABLES: Dict[str, str] = {
    "FLASK_APP": "beebeesee",
    "FLASK_ENV": "development",
}


def debug():
    sp.Popen(
        ["python", "-m", "flask", "run"], env=ENVIRONMENT_VARIABLES
    ).wait()


def deploy():
    sp.Popen(
        [
            "waitress-serve",
            f"--port={DEFAULT_PORT}",
            f"--host={DEFAULT_HOST}",
        ],
        env=ENVIRONMENT_VARIABLES,
    ).wait()
