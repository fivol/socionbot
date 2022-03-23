from typing import Union

from aiogram import executor, types
from aiogram.types import CallbackQuery, Message

from socionbot.bot import dp
from socionbot.soc_engine import soc_engine
from socionbot.utils import callback, answer, back_to

import socionbot.theory  # noqa
import socionbot.testing  # noqa


async def to_menu(mess: Union[CallbackQuery, Message]):
    keyword = [
        [
            types.InlineKeyboardButton('📚 Справочник', callback_data='theory')
        ],
        [
            types.InlineKeyboardButton('🎓 Тестирование', callback_data='testing'),
            # types.InlineKeyboardButton('🧑‍🏫 Подробный гайд', callback_data='guide'),
        ],
        [
            types.InlineKeyboardButton('🤔 Что такое соционика', callback_data='what'),
        ]
    ]

    await answer(mess, soc_engine.get_desc('menu'), keyword)


@dp.callback_query_handler(callback('menu'))
async def menu(cb: types.CallbackQuery):
    await to_menu(cb)


@dp.callback_query_handler()
async def default(cb: types.CallbackQuery):
    await to_menu(cb)


def save_user(line):
    with open('host/users.txt', 'a') as f:
        f.write(line + '\n')


def count_lines(path, unique=False) -> int:
    try:
        with open(path, 'r') as f:
            lines = f.read().split('\n')
            if unique:
                return len(set(lines)) - 1
            return len(lines) - 1
    except:
        return 0


@dp.message_handler(commands=['start'])
async def default(message: types.Message):
    save_user(f'{message.from_user.id}:{message.from_user.username}:{message.from_user.full_name}')
    await to_menu(message)


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    text = '*Статистика*\n\n'
    text += f'Пользователи: {count_lines("host/users.txt", unique=True)}\n'
    text += f'Запросов: {count_lines("host/requests.txt")}'
    keyboard = [
        [back_to('menu')]
    ]
    await answer(message, text, keyboard)


@dp.message_handler()
async def default(message: types.Message):
    print('default')
    await to_menu(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
