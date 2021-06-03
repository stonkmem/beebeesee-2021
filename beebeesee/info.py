from pathlib import Path

PROJECT_NAME: str = "beebeesee"
ROOT_DIR = Path(__file__).parents[1].resolve()
STATIC_DIR = ROOT_DIR / "static"
VIEWS_DIR = ROOT_DIR / "views"
DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_PORT: int = 5000
DEFAULT_DEBUG: bool = True

DOMAIN_NAME: str = "renoirtan.cf"
PRE_PATH: str = "http://{0}/".format(DOMAIN_NAME)
