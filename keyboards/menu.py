from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="/settings", style="primary")],
            [InlineKeyboardButton(text="❌ Удалить контекст", callback_data="/reset", style="danger")], 
        ]
    )
def subscribe():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="😎 Подтвердить покупку", callback_data="/success", style="success"),
             InlineKeyboardButton(text="❌ Вернуть звёзды", callback_data="/return", style="danger")],
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

# def repeat():
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(
#                 text="Повторить последнее сообщение 🔁",
#                 callback_data="repeat"
#             )]
#         ]
#     )