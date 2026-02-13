from google.genai.errors import ClientError
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import CommandStart, Command
from aiohttp import web
import keyboards.menu as menu
import ai.gemini as g
import asyncio
import os

from ai.gemini import gemini_image_chat

from config import BOT_TOKEN, PORT

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


user_settings = {}


def get_settings(user_id: int):
    if user_id not in user_settings:
        user_settings[user_id] = {"mode": "tutor"}


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/menu", description="Главное меню"),
        BotCommand(command="/reset", description="Вся история Франциии удалить..."),
    ]
    await bot.set_my_commands(commands)


# Хранилище контекста
user_context: dict[int, list] = {}


@dp.message(CommandStart())
async def start(message: Message):
    user_context[message.from_user.id] = []
    await message.answer(
        "👋 Привет! Я ИИ-репетитор по математике.\n\n"
        "✏️ Пришли текст задачи или 📷 фото задачи.",
        
        reply_markup=menu.main_menu()
    )


@dp.callback_query(F.data == '/settings')
async def settings(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        '''Настройки бота⚙️''',
        reply_markup=menu.settings_menu())


@dp.callback_query(F.data == '/mode_tutor')
async def settings(callback: CallbackQuery):
    g.user_chats[callback.from_user.id] = []
    await callback.answer(
        "Выбран режим - репетитор⚙️",
        reply_markup=g.get_chat(callback.from_user.id, "tutor"))
    user_settings.clear()
    user_settings[callback.from_user.id] = {"mode": "tutor"}


@dp.callback_query(F.data == '/mode_teacher')
async def settings(callback: CallbackQuery):
    g.user_chats[callback.from_user.id] = []
    await callback.answer(
        "Выбран режим - учитель⚙️",
        reply_markup=g.get_chat(callback.from_user.id, "teacher"))
    user_settings.clear()
    user_settings[callback.from_user.id] = {"mode": "teacher"}


@dp.callback_query(F.data == '/mode_olymp')
async def settings(callback: CallbackQuery):
    g.user_chats[callback.from_user.id] = []
    await callback.answer(
        "Выбран режим - олимпиадник⚙️",
        reply_markup=g.get_chat(callback.from_user.id, "olymp"))
    user_settings.clear()
    user_settings[callback.from_user.id] = {"mode": "olymp"}


@dp.message(Command("reset"))
async def reset_command(message: Message):
    user_context[message.from_user.id] = []
    g.user_chats.pop(message.from_user.id)
    await message.answer("Чат самоуничтожился! Поздравляю!")


@dp.callback_query(F.data == "/reset")
async def reset_callback(callback: CallbackQuery):
    user_context[callback.from_user.id] = []
    await callback.answer("Чат самоуничтожился! Поздравляю!")


@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    mode = user_settings[user_id]
    # Инициализация контекста
    if user_id not in user_context:
        user_context[user_id] = []

    photo = message.photo[-1]  # самое качественное фото
    file = await bot.get_file(photo.file_id)

    #Cкачиваем через Telegram API
    image_bytes = await bot.download(file)

    # Gemini
    msg = await message.answer("🖼️ Обрабатываю запрос...")

    try:
        answer = await gemini_image_chat(
            user_id=user_id,
            mode=mode,
            user_context=user_context[user_id],
            image_bytes=image_bytes.read(),
            prompt=message.text if isinstance(message.text,str) else ''
        )

        user_context[user_id].append({
            "role": "assistant",
            "text": answer if isinstance(answer,str) else ''
        })
        await msg.delete()
        await message.answer(answer, parse_mode="HTML")

    except ClientError as e:
        await msg.delete()
        code = e.code

        if code == 400:
            await message.answer("Попробуйте позже❌")
        elif code == 429:
            await message.answer("Бот перегружен, отправь запрос ещё раз❤️")
        elif code == 503:
            await message.answer("Неполадки с сервером, попробуй через 10-15 минут⏳")
        else:
            await message.answer("❌ Ошибка при обработке запроса.")


@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    mode = user_settings
    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({
        "role": "user",
        "text": message.text
    })

    msg = await message.answer("🖼️ Обрабатываю запрос...")

    try:
        answer = await gemini_image_chat(
            user_id=user_id,
            mode=mode,
            user_context=user_context[user_id],
            image_bytes=None,
            prompt=message.text
        )
        await msg.delete()
        await message.answer(answer, parse_mode="HTML")

        user_context[user_id].append({
            "role": "assistant",
            "text": answer
        })
    except ClientError as e:
        await msg.delete()
        code = e.code

        if code == 400:
            await message.answer("Попробуйте позже❌")
        elif code == 429:
            await message.answer("Бот перегружен, отправь запрос ещё раз❤️")
        elif code == 503:
            await message.answer("Неполадки с сервером, попробуй через 10-15 минут⏳")
        else:
            await message.answer("❌ Ошибка при обработке запроса.")


# @dp.callback_query(F.data == "repeat")
# async def repeat_last_message(callback: CallbackQuery):
#     await callback.answer("Штирлиц играл в карты и проигрался. Но Штирлиц умел делать хорошую мину при плохой игре. Когда Штирлиц покинул компанию, мина сработала.")

#     user_id = callback.from_user.id
#     mode = get_settings(user_id)["mode"]

#     # Проверка контекста
#     if user_id not in user_context or not user_context[user_id]:
#         await callback.message.answer("❌ Нет сообщения для повтора.")
#         return

#     # Ищем последнее сообщение пользователя
#     last_user_message = None
#     for msg in reversed(user_context[user_id]):
#         if msg["role"] == "user":
#             last_user_message = msg["text"]
#             break

#     if not last_user_message:
#         await callback.message.answer("❌ Не удалось найти последнее сообщение.")
#         return

#     msg = await callback.message.answer("🔁 Повторяю запрос...")

#     try:
#         answer = await gemini_image_chat(
#             user_id=user_id,
#             mode=mode,
#             user_context=user_context[user_id],
#             image_bytes=None,
#             prompt=last_user_message
#         )

#         await msg.delete()
#         await callback.message.answer(answer, parse_mode="HTML")

#         # сохраняем ответ в контекст
#         user_context[user_id].append({
#             "role": "assistant",
#             "text": answer
#         })

#     except Exception as e:
#         await msg.delete()
#         await callback.message.answer(
#             "❌ Снова ошибка. Попробуй чуть позже.",
#             reply_markup=menu.repeat()
#         )

async def healthcheck(request):
    return web.Response(text="Bot is alive")


async def run_web_server():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    port = int(PORT)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    await set_bot_commands(bot)
    await run_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())