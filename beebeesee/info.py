from pathlib import Path

PROJECT_NAME: str = "beebeesee"
SERVER_DIR = Path(__file__).parent.resolve()
UPLOAD_DIR = SERVER_DIR / "uploaded"
ROOT_DIR = SERVER_DIR.parent
STATIC_DIR = ROOT_DIR / "static"
VIEWS_DIR = ROOT_DIR / "views"
MODELS_DIR = ROOT_DIR / "models"
DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_PORT: int = 5000
DEFAULT_DEBUG: bool = True

DOMAIN_NAME: str = "renoirtan.cf"
PRE_PATH: str = "http://{0}/".format(DOMAIN_NAME)
