from itertools import islice
from typing import Optional, Union

from aiogram.types import Message, CallbackQuery

from socionbot.templates import Buttons, gen_keyboard


def callback(callback_data: str):
    def filter_func(cb):
        return cb.data == callback_data
    return filter_func


def callback_keys(*keys):
    def filter_func(cb):
        return all(
            f'{key}:' in cb.data
            for key in keys
        ) and len(keys) == len(cb.data.split(' '))
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


def extract_value_from_callback(callback_data: str, key: str):
    return callback_data_to_dict(callback_data)[key]


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
    if message.text != '/start':
        await message.delete()
    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
