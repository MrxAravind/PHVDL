from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.environ.get('TELEGRAM_API', ''))
API_HASH = os.environ.get('TELEGRAM_HASH', '')
DUMP_ID = int(os.environ.get('DUMP_CHAT_ID', ''))
DATABASE = os.getenv("DATABASE")
LOG_ID = int(os.environ.get('LOG_CHAT_ID', ''))
