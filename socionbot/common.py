from aiogram.types import InlineKeyboardButton, CallbackQuery

from socionbot.soc_engine import soc_engine
from socionbot.utils import generate_callback_data, batcher, back_to, extract_value_from_callback, \
    callback_data_to_dict, answer, MAX_TEXT_LEN, paginate, EXTRA_SIZE_LIMIT


async def send_buttons(cb: CallbackQuery, text, extra_buttons=None, line_buttons_amount=4):
    model_name = cb.data
    items = soc_engine.get_all(model_name)
    buttons = []
    for item in items:
        buttons.append(
            InlineKeyboardButton(
                item.name,
                callback_data=generate_callback_data(**{model_name: item.id}, desc=0)
            )
        )

    keyboard_buttons = list(batcher(buttons, line_buttons_amount))
    if extra_buttons:
        keyboard_buttons.append(extra_buttons)
    keyboard_buttons.append([back_to('theory')])
    await answer(
        cb,
        text,
        keyboard=keyboard_buttons
    )


async def send_desc(cb: CallbackQuery, back_route=None):
    model_name = list(set(callback_data_to_dict(cb.data)) - {'desc'})[0]
    item_id = extract_value_from_callback(cb.data, model_name)
    desc_idx = int(extract_value_from_callback(cb.data, 'desc'))
    soc_item = soc_engine.get_item(model_name, item_id)
    text = ''
    text += f'*{soc_item.get_full_name()}*\n'

    desc = 'Coming soon...'
    if soc_item.desc:
        desc = soc_engine.get_soc_model_desc(soc_item, desc_idx).text

    if len(desc) > MAX_TEXT_LEN + EXTRA_SIZE_LIMIT:
        cb.data = generate_callback_data(model=model_name, page=0, item=soc_item.id, desc=desc_idx)
        await desc_page(cb)
        return

    text += f'\n{desc}'

    buttons = []

    for i, desc_item in enumerate(soc_engine.get_soc_model_desc_list(soc_item)):
        if i == desc_idx:
            continue
        buttons.append(
            InlineKeyboardButton(
                desc_item.label or f'Описание {i + 1}',
                callback_data=generate_callback_data(desc=i, **{model_name: soc_item.id})
            )
        )
    await answer(
        cb, text,
        keyboard=[
            *list(batcher(buttons, 3)),
            [back_to(back_route or model_name)]
        ]
    )


async def desc_page(cb: CallbackQuery):
    desc_idx = int(extract_value_from_callback(cb.data, 'desc'))
    model_name = extract_value_from_callback(cb.data, 'model')
    item_id = extract_value_from_callback(cb.data, 'item')
    page_num = int(extract_value_from_callback(cb.data, 'page'))
    item = soc_engine.get_item(model_name, item_id)

    model = soc_engine.get_item(model_name, item_id)
    desc_elem = soc_engine.get_soc_model_desc(model, desc_idx)
    pages = paginate(desc_elem.text)

    text = f'*{item.get_full_name()}*\n'
    text += f'_{desc_elem.label}_ (стр {page_num + 1} / {len(pages)})\n\n{pages[page_num]}'
    buttons = []
    if page_num > 0:
        buttons.append(
            InlineKeyboardButton(
                '⬅️ Предыдущая',
                callback_data=generate_callback_data(page=page_num - 1, model=model_name, desc=desc_idx, item=item_id)
            )
        )
    if page_num < len(pages) - 1:
        buttons.append(
            InlineKeyboardButton(
                'Следующая ➡️️',
                callback_data=generate_callback_data(page=page_num + 1, model=model_name, desc=desc_idx, item=item_id)
            )
        )
    else:
        buttons.append(
            InlineKeyboardButton(
                '⬆️ Вернуться к типу',
                callback_data=generate_callback_data(**{model_name: item.id, 'desc': 0})
            )
        )

    keyword = [
        buttons,
        [back_to(**{model_name: item.id, 'desc': 0})]
    ]
    await answer(
        cb, text, keyboard=keyword
    )
