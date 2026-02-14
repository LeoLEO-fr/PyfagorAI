from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="/settings", style="primary")]
        ]
    )

def settings_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌿 Режим: Репетитор", callback_data="/mode_tutor")],
            [InlineKeyboardButton(text="⭐ Режим: Учитель", callback_data="/mode_teacher")],
            [InlineKeyboardButton(text="🔥 Режим: Олимпиадник", callback_data="/mode_olymp")],
        ]
    )

def repeat():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Повторить последнее сообщение 🔁",
                callback_data="repeat"
            )]
        ]
    )