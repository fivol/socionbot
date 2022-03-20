from aiogram.types import CallbackQuery, InlineKeyboardButton

from socionbot.common import send_buttons, send_desc, desc_page
from socionbot.constants import what_is_socion
from socionbot.bot import dp
from socionbot.soc_engine import soc_engine
from socionbot.templates import to_menu_keyboard, Buttons, gen_keyboard
from socionbot.theory_models import SocDichotomyValue
from socionbot.utils import callback, callback_keys, answer, extract_value_from_callback, generate_callback_data, \
    back_to, paginate

import relations  # noqa


@dp.callback_query_handler(callback('theory'))
async def theory(cb: CallbackQuery):
    keyboard = gen_keyboard(
        [
            [Buttons.types],
            [
                InlineKeyboardButton('🤝 Отношения', callback_data='relations-first'),
            ],
            [
                InlineKeyboardButton('📦 Функции', callback_data='func'),
                InlineKeyboardButton('☘️ Аспекты', callback_data='aspect'),
                InlineKeyboardButton('☑️ Дихотомии', callback_data=generate_callback_data(d=0, d_list='')),
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
async def soc_type_handler(cb: CallbackQuery):
    await send_desc(cb)


@dp.callback_query_handler(callback_keys('d', 'd_list'))
async def soc_dichotomy(cb: CallbackQuery):
    dichotomies = soc_engine.get_all_dichotomies()
    d_list = extract_value_from_callback(cb.data, 'd_list')

    answers = d_list.strip(',').split(',')
    if len(answers) >= 4:
        dichotomies = [SocDichotomyValue(ans) for ans in answers]
        soc_type = soc_engine.get_type_by_dichotomies(dichotomies)
        cb.data = generate_callback_data(type=soc_type.id, desc=0)
        await send_desc(cb, back_route=generate_callback_data(d=0, d_list=''))
        return

    dichotomy_idx = int(extract_value_from_callback(cb.data, 'd'))
    dichotomy = dichotomies[dichotomy_idx]

    first, second = dichotomy.name.split(' ')
    first_id, second_id = dichotomy.id.split('-')
    buttons = [
        InlineKeyboardButton(
            first,
            callback_data=generate_callback_data(d=dichotomy_idx + 1, d_list=f'{first_id},{d_list}')),
        InlineKeyboardButton(
            second,
            callback_data=generate_callback_data(d=dichotomy_idx + 1, d_list=f'{second_id},{d_list}'))
    ]

    keyword = [
        buttons,
        [InlineKeyboardButton('📖 Описание дихотомий', callback_data='dichotomy')],
        [back_to('theory')]
    ]
    text = f'Выберете среди дихотомий чтобы определить соционический тип: {first} / {second}'
    await answer(
        cb, text, keyword
    )


@dp.callback_query_handler(callback_keys('desc', 'model', 'page', 'item'))
async def desc_read_page(cb: CallbackQuery):
    await desc_page(cb)
