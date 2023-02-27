import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent
PATH_TO_VOSK_MODEL = BASE_DIR / "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15"
DATABASE = os.getenv("DATABASE", "")

PATH_TO_TTS_MODEL = "/usr/local/lib/python3.10/site-packages/TTS/.models.json"
# PATH_TO_TTS_MODEL = "/lesa/venv/lib/python3.10/site-packages/TTS/.models.json"

DATE_FORMAT = "%d.%m.%Y"

DEBUG = os.getenv("DEBUG", "")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {name} {levelname} {module} {process:d} {thread:d} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "log/general.log",
            'maxBytes': 10000000,
            'backupCount': 20,
            'level': 'WARNING',
            'formatter': 'verbose',
        },
        'info': {
            'level': 'INFO',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        '': {
            'level': 'WARNING' if DEBUG == 'False' else 'INFO',
            'handlers': ['default' if DEBUG == 'False' else 'info'],
        }
    },
}

