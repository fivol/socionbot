from aiogram.types import CallbackQuery, InlineKeyboardButton

from socionbot.bot import dp
from socionbot.common import send_buttons, send_desc
from socionbot.soc_engine import soc_engine
from socionbot.templates import gen_keyboard
from socionbot.utils import callback, batcher, generate_callback_data, callback_keys, \
    extract_value_from_callback, back_to, answer


@dp.callback_query_handler(callback('relations-first'))
async def relations_first_handler(cb: CallbackQuery):
    buttons = []
    for item in soc_engine.get_all_types():
        buttons.append(
            InlineKeyboardButton(
                item.name,
                callback_data=generate_callback_data(first=item.id)
            )
        )

    keyword = gen_keyboard(
        [
            *list(batcher(buttons, 4)),
            [back_to('relation')]
        ]
    )
    text = 'Выберите первый тип'
    await answer(
        cb,
        text,
        keyboard=keyword
    )


@dp.callback_query_handler(callback_keys('first'))
async def relations_second_handler(cb: CallbackQuery):
    first_type = soc_engine.get_type(extract_value_from_callback(cb.data, 'first'))

    buttons = []
    for second_type in soc_engine.get_all_types():
        relation = soc_engine.get_relation_by_types(first_type, second_type)
        button_text = f'{second_type.name}: {relation.name.lower()}'
        buttons.append(
            InlineKeyboardButton(
                button_text,
                callback_data=generate_callback_data(first=first_type.id, second=second_type.id)
            )
        )

    keyword = gen_keyboard(
        [
            *list(batcher(buttons, 2)),
            [back_to('relation')]
        ]
    )
    text = 'Выберите второй тип'
    await answer(
        cb,
        text,
        keyboard=keyword
    )


@dp.callback_query_handler(callback_keys('first', 'second'))
async def relation_by_types(cb: CallbackQuery):
    first_type = soc_engine.get_type(extract_value_from_callback(cb.data, 'first'))
    second_type = soc_engine.get_type(extract_value_from_callback(cb.data, 'second'))
    relation = soc_engine.get_relation_by_types(first_type, second_type)
    cb.data = generate_callback_data(desc=0, relation=relation.id)
    await send_desc(cb)


@dp.callback_query_handler(callback('relation'))
async def relations_handler(cb: CallbackQuery):
    text = """Выберите из списка интертипных отношений в соционике или найдите их по двум типам"""
    extra_button = InlineKeyboardButton('Определить по типам', callback_data='relations-first')
    await send_buttons(cb, text, extra_buttons=[extra_button])


@dp.callback_query_handler(callback_keys('relation', 'desc'))
async def relation_handler(cb: CallbackQuery):
    await send_desc(cb)
