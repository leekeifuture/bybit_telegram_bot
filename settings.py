from ast import literal_eval
from os import environ

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_CHAT_ID = int(environ.get('TELEGRAM_CHAT_ID'))

TELEGRAM_ADMINS = literal_eval(environ.get('TELEGRAM_ADMINS'))

TELEGRAM_BOT_TOKEN = environ.get('TELEGRAM_BOT_TOKEN')

API_ID = environ.get('API_ID')
API_HASH = environ.get('API_HASH')
SESSION_STRING = environ.get('SESSION_STRING')

LOG_LEVEL = environ.get("LOG_LEVEL", "INFO").upper()
