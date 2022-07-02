from os import environ

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_CHAT_ID = int(environ.get('TELEGRAM_CHAT_ID'))

TELEGRAM_BOT_TOKEN = environ.get('TELEGRAM_BOT_TOKEN')

API_ID = environ.get('API_ID')
API_HASH = environ.get('API_HASH')

TIMEOUT_MIRRORING = float(environ.get('TIMEOUT_MIRRORING', '900'))
LIMIT_TO_WAIT = int(environ.get('LIMIT_TO_WAIT', '50'))
SESSION_STRING = environ.get('SESSION_STRING')

API_KEI = environ.get('API_KEI')
API_SECRET = environ.get('API_SECRET')

LOG_LEVEL = environ.get("LOG_LEVEL", "INFO").upper()
