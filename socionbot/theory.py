from aiogram.types import CallbackQuery, InlineKeyboardButton

from socionbot.common import send_buttons, send_desc
from socionbot.constants import what_is_socion
from socionbot.bot import dp
from socionbot.templates import to_menu_keyboard, Buttons, gen_keyboard
from socionbot.utils import callback, callback_keys, answer

import relations  # noqa


@dp.callback_query_handler(callback('theory'))
async def theory(cb: CallbackQuery):
    keyboard = gen_keyboard(
        [
            [
                Buttons.types,
                InlineKeyboardButton('🤝 Отношения', callback_data='relation'),
            ],
            [
                InlineKeyboardButton('📦 Функции', callback_data='func'),
                InlineKeyboardButton('☘️ Аспекты', callback_data='aspect'),
                InlineKeyboardButton('☑️ Дихотомии', callback_data='dichotomy'),
            ],
            [
                Buttons.menu
            ]
        ]
    )
    text = 'Просматривайте описание ТИМ-ов, функций, аспектов, ' \
           'отношений и дихотомий в удобном интерактивном формате'
    await answer(
        cb,
        text,
        keyboard=keyboard
    )


@dp.callback_query_handler(callback('what'))
async def what_is(cb: CallbackQuery):
    await answer(
        cb,
        what_is_socion,
        to_menu_keyboard
    )


@dp.callback_query_handler(callback('dichotomy'))
async def dichotomies_handler(cb: CallbackQuery):
    text = 'Что-то про дихотомии'
    await send_buttons(cb, text, line_buttons_amount=2)


@dp.callback_query_handler(callback_keys('dichotomy', 'desc'))
async def dichotomy_handler(cb: CallbackQuery):
    await send_desc(cb)


@dp.callback_query_handler(callback('func'))
async def funcs_handler(cb: CallbackQuery):
    text = 'Что-то про функции'
    await send_buttons(cb, text)


@dp.callback_query_handler(callback_keys('func', 'desc'))
async def func_handler(cb: CallbackQuery):
    await send_desc(cb)


@dp.callback_query_handler(callback('aspect'))
async def aspects(cb: CallbackQuery):
    text = 'Соционические аспекты'
    await send_buttons(cb, text, line_buttons_amount=2)


@dp.callback_query_handler(callback_keys('aspect', 'desc'))
async def aspect(cb: CallbackQuery):
    await send_desc(cb)


@dp.callback_query_handler(callback('type'))
async def types_handler(cb: CallbackQuery):
    text = 'Выберите один из типов ниже, чтобы прочитать подробное описание, ' \
           'посмотреть примеры известных людей - представителей типа и отношений с другими ТИМ-ами'
    await send_buttons(cb, text)


@dp.callback_query_handler(callback_keys('type', 'desc'))
async def soc_type(cb: CallbackQuery):
    await send_desc(cb)
