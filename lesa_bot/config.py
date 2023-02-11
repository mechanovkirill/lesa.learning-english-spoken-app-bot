import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR / "db.sqlite3"
TEMPLATES_DIR = BASE_DIR / "templates"

DATE_FORMAT = "%d.%m.%Y"

DEBUG = os.getenv("DEBUG", bool)

if DEBUG:
    level = 'INFO'
    handler = 'info'
level = 'WARNING'
handler = 'default'

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
            'filename': 'logs/''general.log',
            'maxBytes': 10000000,
            'backupCount': 20,
            'level': 'INFO',
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
            'level': f'{level}',
            'handlers': [f'{handler}'],
        }
    },
}




