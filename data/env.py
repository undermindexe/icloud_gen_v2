from dotenv import load_dotenv
import os
import sys
from pathlib import Path


if getattr(sys, 'frozen', False):
    base_dir = Path(sys.executable).parent
else:
    base_dir = Path(__file__).parent

env_path = base_dir / '.env'

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