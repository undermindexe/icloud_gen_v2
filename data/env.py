from dotenv import load_dotenv
import os
from pathlib import Path


env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def get_bool(name: str, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")

def get_int(name: str, default=0):
    value = os.getenv(name)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def get_str(name: str, default=""):
    return os.getenv(name, default)

HIDDEN_MODE = get_bool('HIDDEN_MODE')
PROXY_MODE = get_bool('PROXY_MODE')
DEBUG = get_bool('DEBUG')