from aiogram import executor, types

from socionbot.constants import menu_text, help_text

from socionbot.bot import dp
from socionbot.templates import to_menu_keyboard
from socionbot.utils import callback, answer

import socionbot.theory  # noqa
import socionbot.testing  # noqa


async def help_message(message: types.Message):
    await answer(message, help_text, to_menu_keyboard)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await help_message(message)


@dp.callback_query_handler(callback('help'))
async def help(cb: types.CallbackQuery):
    await help_message(cb.message)


async def to_menu(message: types.Message):
    keyword = [
        [
            types.InlineKeyboardButton('🤔 Что такое соционика', callback_data='what'),
            types.InlineKeyboardButton('🧑‍🏫 Подробный гайд', callback_data='guide'),
        ],
        [
            types.InlineKeyboardButton('📚 Справочник', callback_data='theory'),
            types.InlineKeyboardButton('🎓 Тестирование', callback_data='testing'),
        ]
    ]

    await answer(message, menu_text, keyword)


@dp.callback_query_handler(callback('menu'))
async def menu(cb: types.CallbackQuery):
    await to_menu(cb.message)


@dp.callback_query_handler()
async def default(cb: types.CallbackQuery):
    print('Default callback', cb.data)
    await to_menu(cb.message)


@dp.message_handler()
async def default(message: types.Message):
    await to_menu(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
