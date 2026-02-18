import asyncio
from datetime import datetime, timedelta
from bot import now
from google import genai
from google.genai.chats import Chat
from google.genai.types import Part as P
from config import GEMINI_API_KEY, id, id1
from ai.prompts import (
    BASE_PROMPT,
    MODE_PROMPTS,
    ADMIN_MODE
)


Admins_IDs = {id:"never", id1:"never"}


async def remove_expired_daily():
    while True:
        for user_id in list(Admins_IDs.keys()):
            if Admins_IDs[user_id] <= now:
                del Admins_IDs[user_id]
                print(f"Пользователь {user_id} удалён, подписка закончилась")
        print("Проверка завершена")
        
        # ждём 24 часа (24*60*60 секунд)
        await asyncio.sleep(24 * 60 * 60)

# пример запуска
async def main():
    # здесь можно добавлять новых пользователей
    await remove_expired_daily()

asyncio.run(main())



client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemma-3-27b-it"



user_chats = {}


def get_chat(user_id: int, mode: str):

    if user_id not in user_chats and user_id not in Admins_IDs :
        history = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": BASE_PROMPT + "\n" + MODE_PROMPTS.get(mode, "")
                    }
                ]
            }
        ]
        user_chats[user_id] = client.chats.create(history=history, model=MODEL)

    if user_id not in user_chats and user_id in Admins_IDs:
        history = [
            {
                "role": "user",
                "parts": [
                    {
                        "text":  ADMIN_MODE +"\n" + MODE_PROMPTS.get(mode, "")
                    }
                ]
            }
        ]
        user_chats[user_id] = client.chats.create(history=history, model=MODEL)

    return user_chats[user_id]


def reset_chat(user_id: int):
    """Сброс контекста"""
    if user_id in user_chats:
        del user_chats[user_id]


def send_message(user_id: int, text: str, mode: str) -> str:
    chat: Chat = get_chat(user_id, mode)
    response = chat.send_message(text)
    return response.text.strip()


async def gemini_image_chat(user_id, mode,user_context, image_bytes, prompt) -> str:
    
    chat: Chat = get_chat(user_id, mode)

    # История
    texts = []
    for msg in user_context[-10:]:
        texts.append(msg["text"])

    texts.append(prompt)
    final_text = "\n".join(texts)

    if image_bytes:
        response = chat.send_message([
            P.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            final_text
        ])
    else:
        response = chat.send_message(final_text)

    return response.text.strip()