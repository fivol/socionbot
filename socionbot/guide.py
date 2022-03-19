from aiogram import types

from socionbot.bot import dp
from socionbot.utils import callback


@dp.callback_query_handler(callback('guide'))
async def guide_handler(cb: types.CallbackQuery):
    pass
