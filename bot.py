from google.genai.errors import ClientError
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command
from aiohttp import web
from aiogram.enums import ContentType
import keyboards.menu as menu
import ai.gemini as g
import asyncio
import os

from ai.gemini import gemini_image_chat

from config import BOT_TOKEN, PORT

PROVIDER_TOKEN = ""
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


user_settings = {}


def get_settings(user_id: int,):
    if user_id not in user_settings:
        user_settings[user_id] = {"mode": "tutor"}

    return user_settings[user_id]


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/menu", description="Главное меню"),

    ]
    await bot.set_my_commands(commands)


# Хранилище контекста
user_context: dict[int, list] = {}


@dp.message(CommandStart())
async def start(message: Message):
    user_context[message.from_user.id] = []
    await message.answer(
        "👋 Привет! Я ИИ-репетитор по математике.\n\n"
        "✏️ Пришли текст задачи или 📷 фото задачи."
    )
    await message.answer(
        "👋 Добро пожаловать в главное меню\n\n"
        "✏️ Меню находится в разработке.\n\n"
        "😎Совсем скоро здесь может появиться что-то новое",
        
        reply_markup=menu.main_menu()
    )


@dp.message(F.data == "/buy")
async def subscribe(callback: CallbackQuery):
    await callback.message.answer(
        "❤️‍🔥 Если ты нажал кнопку, это значит, что ты хочешь подписку. \n\n"
        """⚙️ С подпиской у тебя появляется возможность:
        1. Получать объяснения на все предметы, в том числе университетского уровня
        2. Получать анаиз своих ошибок
        3. Получать рассписанную логику работы по шагам максимально подробно
        4. Решать задачи альтернативными методами. \n\n"""
        "😏 Но ответов конечно мы тебе не дадим)",

        reply_markup=menu.subscribe()
    )


@dp.message(F.data == "/success")
async def success(message: Message):
    prices = [LabeledPrice(label="Подписка", amount=100)]

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Покупка подписки",
        description="Доступ к PRO режиму",
        payload="pro_subscription",
        provider_token=PROVIDER_TOKEN,
        currency="XTR",  # Stars валюта
        prices=prices,
    )


@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    await message.answer("Оплата прошла успешно 🚀")



@dp.callback_query(F.data == '/settings')
async def settings(callback: CallbackQuery):
    await callback.message.answer(
        '''Настройки бота⚙️''',
        reply_markup=menu.settings_menu())


@dp.callback_query(F.data == "/reset")
async def reset_callback(callback: CallbackQuery):
    user_context[callback.from_user.id] = []
    await callback.message.answer("Чат самоуничтожился! Поздравляю!")


@dp.callback_query(Command == 'menu')
async def menu_return(callback: CallbackQuery):
    await callback.message.answer(
        "👋 Привет! И добро пожаловать в главное меню\n\n"
        "✏️ Меню находится в разработке.\n\n"
        "😎Совсем скоро здесь может появиться что-то новое",
        
        reply_markup=menu.main_menu()
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    mode = get_settings(user_id)["mode"]
    # Инициализация контекста
    if user_id not in user_context:
        user_context[user_id] = []

    photo = message.photo[-1]  # самое качественное фото
    file = await bot.get_file(photo.file_id)

    image_bytes = await bot.download(file)

    msg = await message.answer("🖼️ Обрабатываю запрос...")

    try:
        answer = await gemini_image_chat(
            user_id=user_id,
            mode=mode,
            user_context=user_context[user_id],
            image_bytes=image_bytes.read(),
            prompt=message.text if isinstance(message.text,str) else ''
        )

        await msg.delete()
        await message.answer(answer, parse_mode="HTML")

        user_context[user_id].append({
            "role": "assistant",
            "text": answer if isinstance(answer,str) else ''
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


@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    mode = get_settings(user_id)["mode"]
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