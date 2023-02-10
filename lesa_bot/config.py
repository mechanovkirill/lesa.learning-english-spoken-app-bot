import os
from pathlib import Path

from dotenv import load_dotenv
import logging

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR / "db.sqlite3"
TEMPLATES_DIR = BASE_DIR / "templates"

DATE_FORMAT = "%d.%m.%Y"


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO, filename='general.log'
)
logger = logging.getLogger(__name__)

