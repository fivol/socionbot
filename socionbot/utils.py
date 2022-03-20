import json
from itertools import islice
from typing import Union

from aiogram.types import Message, CallbackQuery

from socionbot.templates import Buttons, gen_keyboard


MAX_TEXT_LEN = 700
EXTRA_SIZE_LIMIT = 200


def callback(callback_data: str):
    def filter_func(cb):
        return cb.data == callback_data
    return filter_func


def callback_keys(*keys, **optional_keys):
    def filter_func(cb):
        if ':' not in cb.data:
            return False
        data_dict = callback_data_to_dict(cb.data)
        for key in data_dict:
            if key not in keys and key not in optional_keys:
                return False
        for key in keys:
            if key not in data_dict:
                return False
        return True
    return filter_func


def generate_callback_data(**data):
    return ' '.join([f'{key}:{value}' for key, value in data.items()])


def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


def callback_data_to_dict(callback_data):
    return {
        item.split(':')[0]: item.split(':')[1]
        for item in callback_data.split(' ')
    }


def extract_value_from_callback(callback_data: str, key: str, default=None):
    return callback_data_to_dict(callback_data).get(key, default)


def back_to(callback_data=None, **data):
    back = Buttons.back
    if callback_data:
        back.callback_data = callback_data
        return back
    back.callback_data = generate_callback_data(**data)
    return back


async def answer(message: Union[Message, CallbackQuery], text, keyboard=None):
    if isinstance(keyboard, list):
        keyboard = gen_keyboard(keyboard)
    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message

    if message.text == '/start':
        await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    elif message.from_user.id != message.bot.id:
        await message.delete()
    else:
        if message.text.strip() == text.strip():
            return
        if message.reply_markup and keyboard:
            if message.reply_markup.as_json() == keyboard.as_json():
                return
        await message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)


def get_page(text: str):
    if len(text) < MAX_TEXT_LEN + EXTRA_SIZE_LIMIT:
        return text

    idx = MAX_TEXT_LEN - 1
    while idx > 1 and text[idx] != ' ':
        idx -= 1

    while idx < len(text) and text[idx] in '.!,':
        idx += 1

    return text[:idx]


def paginate(text):
    pages = []
    while text:
        page = get_page(text)
        text = text[len(page):]
        pages.append(page.strip())
    return pages


def read_file(file_name: str):
    with open(file_name, 'r') as f:
        return json.loads(f.read())
