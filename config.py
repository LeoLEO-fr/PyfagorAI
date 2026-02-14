import os
from dotenv import load_dotenv

load_dotenv()

id = os.getenv("id")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = os.getenv("PORT")
if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ BOT_TOKEN или GEMINI_API_KEY не найдены")