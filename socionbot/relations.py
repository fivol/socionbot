from aiogram.types import CallbackQuery, InlineKeyboardButton

from socionbot.bot import dp
from socionbot.common import send_buttons, send_desc
from socionbot.soc_engine import soc_engine
from socionbot.utils import callback, batcher, generate_callback_data, callback_keys, \
    extract_value_from_callback, back_to, answer


@dp.callback_query_handler(callback('relations-first'))
async def relations_first_handler(cb: CallbackQuery):
    buttons = []
    for item in soc_engine.get_all_types():
        buttons.append(
            InlineKeyboardButton(
                f'{item.name}',
                callback_data=generate_callback_data(first=item.id, extended='')
            )
        )

    keyword = [
        *list(batcher(buttons, 4)),
        [InlineKeyboardButton('📖 Описание отношений', callback_data='relation')],
        [back_to('theory')]
    ]
    text = '1️⃣ Выберите ПЕРВЫЙ тип 1️⃣'
    await answer(
        cb,
        text,
        keyboard=keyword
    )


@dp.callback_query_handler(callback_keys('first', 'extended'))
async def relations_second_handler(cb: CallbackQuery):
    extended = extract_value_from_callback(cb.data, 'extended')
    first_type = soc_engine.get_type(extract_value_from_callback(cb.data, 'first'))

    buttons = []
    for second_type in soc_engine.get_all_types():
        relation = soc_engine.get_relation_by_types(first_type, second_type)
        button_text = f'{second_type.name}'
        if extended:
            button_text = f'{second_type.name.upper()}: {relation.name.lower()}'
        buttons.append(
            InlineKeyboardButton(
                button_text,
                callback_data=generate_callback_data(first=first_type.id, second=second_type.id)
            )
        )

    if not extended:
        extended_btn = InlineKeyboardButton('📊 Расширенный вид',
                                            callback_data=generate_callback_data(first=first_type.id, extended='yes'))
    else:
        extended_btn = InlineKeyboardButton('📊 Упрощенный вид',
                                            callback_data=generate_callback_data(first=first_type.id, extended=''))

    keyword = [
        *list(batcher(buttons, 4 if not extended else 2)),
        [extended_btn],
        [back_to('relations-first')]
    ]
    text = '2️⃣ Выберите ВТОРОЙ тип 2️⃣'
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
    await send_desc(cb, back_route=generate_callback_data(first=first_type.id, extended=''))


@dp.callback_query_handler(callback('relation'))
async def relations_handler(cb: CallbackQuery):
    await send_buttons(cb, soc_engine.get_desc('relations'))


@dp.callback_query_handler(callback_keys('relation', 'desc'))
async def relation_handler(cb: CallbackQuery):
    await send_desc(cb)
