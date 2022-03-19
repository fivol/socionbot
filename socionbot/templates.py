from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Buttons:
    menu = InlineKeyboardButton('☰ Меню', callback_data='menu')
    back = InlineKeyboardButton('⬅ Назад', callback_data='back')
    types = InlineKeyboardButton('📝 Типы', callback_data='type')


to_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[Buttons.menu]]
)


def gen_keyboard(buttons):
    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
