import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USERT")
DB_PASSWORD = os.getenv("DB_PASSWORD")
id = os.getenv("id")
id1 = os.getenv("id1")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = os.getenv("PORT")
if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ BOT_TOKEN или GEMINI_API_KEY не найдены")