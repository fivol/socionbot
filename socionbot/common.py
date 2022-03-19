from aiogram.types import InlineKeyboardButton, CallbackQuery

from socionbot.soc_engine import soc_engine
from socionbot.utils import generate_callback_data, batcher, back_to, extract_value_from_callback, \
    callback_data_to_dict, answer


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


async def send_desc(cb: CallbackQuery):
    model_name = list(set(callback_data_to_dict(cb.data)) - {'desc'})[0]
    item_id = extract_value_from_callback(cb.data, model_name)
    desc_idx = int(extract_value_from_callback(cb.data, 'desc'))
    soc_item = soc_engine.get_item(model_name, item_id)
    text = ''
    text += f'*{soc_item.get_full_name()}*\n'

    desc = 'Coming soon...'
    if soc_item.desc:
        desc = soc_item.desc[desc_idx].text

    text += f'\n\n{desc}'

    buttons = []

    for i, desc_item in enumerate(soc_item.desc[1:]):
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
            [back_to(model_name)]
        ]
    )
