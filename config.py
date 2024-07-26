from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.environ.get('API_ID', ''))
API_HASH = os.environ.get('API_HASH', '')
LINK_ID = int(os.environ.get('LINK_CHAT_ID', ''))
DATABASE = os.getenv("DATABASE")
LOG_ID = int(os.environ.get('LOG_CHAT_ID', ''))
DUMP_ID = int(os.environ.get('DUMP_CHAT_ID', ''))
